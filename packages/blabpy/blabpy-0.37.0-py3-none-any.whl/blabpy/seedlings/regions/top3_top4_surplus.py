"""
Here, we first match all tokens to regions they are in and then decide whether they are surplus, top_3_hours, or
top_4_hours.

# Surplus

Surplus regions were marked manually in the cha files.

# top_3_hours/top_4_hours

For both of those we want to find annotated regions that are top N with respect to their cvc-awc rank. If
there were no skips or silences, we could just take N highest ranked subregions. However, there are skips and
silences, so we will need to use makeup (incl. extra) regions as well. We won't be assigning makeup regions to the
subregions they are making up for because (a) it's too complicated, (b) some makeup regions are not making up for a
specific subregion but for the whole recording. Instead, we will sort makeup regions chronologically and then take
as many of those as we need to get to N hours. If the last region overshoots the target duration, we will cut it to
have exactly N hours.

Month 06 and 07 are special because they were annotated throughout and the subregions we are using  are the subregions
we would have created if we were not going to annotated the whole recording. They also don't have makeup regions. So,
we'll approximate what an annotator would have done if the first N subregions had more that 15 minutes missing: we'll
first take the missing time from the subregion N+1. If that's not enough, we'll take the missing time from the subregion
N+2. This is different from what we do for months 08-13 because we are making up for missing time in the order of rank,
not in the order of onset time. So, we can't just mark subregions (N+1)+ as makeup and apply exactly the same logic.

Here is a table summarizing all relevant month-N combinations:

+-------+----------------------+----------------------+
| month | top_3_hours          | top_4_hours          |
+-------+----------------------+----------------------+
| 06-07 | procedure            | procedure            |
+-------+----------------------+----------------------+
| 08-13 | procedure            | subregions + makeups |
+-------+----------------------+----------------------+
| 14-17 | subregions + makeups | NA                   |
+-------+----------------------+----------------------+

This table is implemented in the function select_top_n_regions.

Here is the "procedure" step by step:
- Calculate total duration of N highest-ranked subregions. If it gets us within 15 minutes of N hours, use those
    subregions and ignore makeup regions.
- If it is less than N hours minus 15 minutes:
  - Find regions that we can potentially use for top N regions.
    - Subregions with rank up to N.
    - Makeup regions:
        - For months 06 and 07, these are subregions N+1, [N+2], sorted by rank.
        - For months 08-13, these are makeup regions sorted by onset time.
  - Take regions from the list above one by one until we get to at least N hours minus 15 minutes.
  - Possibly cut the last region to get exactly N hours in total - if there is more than that.

This "procedure" is implemented in the function _apply_makeup_procedure.

TODO:
 Discuss:
 - Should I aim to get at least N hours or N hours minus 15 minutes is enough?
 - Should the answer to the previous question depend on whether I got 2:45+ using only subregions 1-3 or not?
 - If the last makeup region gets total duration to more than N hours, should I take up to N hours plus 15 minutes?
"""
import numpy as np
import pandas as pd

from blabpy.seedlings.listened_time import RegionType, _remove_overlaps_from_other_regions


def _filter_listened_to_regions(processed_regions):
    listened_to_region_types = [RegionType.SUBREGION.value, RegionType.MAKEUP.value, RegionType.EXTRA.value]
    return processed_regions.loc[lambda df: df.region_type.isin(listened_to_region_types)]


def _get_boundary_durations(n_hours):
    """
    We want to get exactly n_hours, but getting within n_hours - 15 minutes and n_hours + 15 minutes is also OK.
    This function calculates these three boundary durations in milliseconds.
    :param n_hours: 3/4
    :return: target_ms, at_least_ms, at_most_ms
    """
    minute_ms = 60 * 1000
    target_ms = n_hours * 60 * minute_ms
    at_least_ms = target_ms - 15 * minute_ms
    at_most_ms = target_ms + 15 * minute_ms

    return target_ms, at_least_ms, at_most_ms


def _add_duration(regions_df):
    return regions_df.assign(duration=lambda df: df.end - df.start)


def _apply_makeup_procedure(regions_processed_df, n_hours: int, month: str):
    """
    See the module docstring for the procedure.
    :param regions_processed_df:
    :param n_hours: 3-4
    :param month: 6-13
    :return:
    """
    assert 6 <= int(month) <= 13, f'Unexpected month to apply the makeup procedure to: {month}'
    assert n_hours in [3, 4], f'Only top 3 and top 4 hours are implemented, got: {n_hours}'
    target_ms, at_least_ms, at_most_ms = _get_boundary_durations(n_hours)

    # Just taking the top N subregions might be enough, then we'll just assign them to be top_n.
    _is_top_n_subregion = (regions_processed_df.region_type.eq('subregion')
                           & (regions_processed_df.subregion_rank <= n_hours))
    subregions_duration = (regions_processed_df
                           .loc[_is_top_n_subregion]
                           .pipe(_add_duration).duration.sum())
    if subregions_duration >= at_least_ms:
        return regions_processed_df[_is_top_n_subregion]

    # Keep listened to regions only
    potential_regions_df = _filter_listened_to_regions(regions_processed_df)

    # First, we'll use subregions ordered by rank, then the makeup regions ordered by onset time.
    potential_regions_df = (
        potential_regions_df
        # 1000 is a magic number, it's just a number that is bigger than any subregion rank
        .assign(sort_key=lambda df: df.subregion_rank.where(df.region_type == 'subregion', other=1000))
        .sort_values(by=['sort_key', 'start'], ascending=True)
        .drop(columns=['sort_key']))

    # Find the first region that gets us to at least n_hours minus 15 minutes. This will be the last region that we
    # select.
    regions_with_at_least_or_more = (potential_regions_df
                                     .pipe(_add_duration)
                                     .assign(cumulative_duration=lambda df: df.duration.cumsum())
                                     .loc[lambda df: df.cumulative_duration >= at_least_ms]
                                     .index)

    # If we don't have enough time even if we take all the regions - let's just take all the regions.
    if len(regions_with_at_least_or_more) == 0:
        return potential_regions_df

    first_region_with_at_least = regions_with_at_least_or_more[0]
    selected_regions = potential_regions_df.loc[:first_region_with_at_least].copy()

    # Crop the last region so that the total duration is at most n_hours
    total_duration = selected_regions.pipe(_add_duration).duration.sum()
    overshoot = max(total_duration - target_ms, 0)
    selected_regions.loc[first_region_with_at_least, 'end'] -= overshoot

    return selected_regions


TOP_3_KIND = 'top_3'
TOP_4_KIND = 'top_4'
SURPLUS_KIND = 'surplus'


def _standardize_regions(selected_regions, kind):
    """
    Standardize the regions so that they contain only the necessary information and are consistently sorted.
    :param selected_regions: output of either
    :param kind: top_3, top_4, or surplus
    :return:
    """
    return (selected_regions
            .assign(kind=kind)
            .convert_dtypes()
            [['kind', 'start', 'end']]
            # start and end might have NAs in surplurs regions for months 6 and 7
            .assign(start_notnull=lambda df: df.start.fillna(0),
                    end_notnull=lambda df: df.end.fillna(df.start.max() + 1))
            .sort_values(by=['start_notnull', 'end_notnull'])
            .drop(columns=['start_notnull', 'end_notnull'])
            .reset_index(drop=True))


def get_top_n_regions(processed_regions, month, n_hours):
    """
    Given a dataframe with regions, return a dataframe with regions that belong to top N hours. See this script's
    docstring for details.
    """
    assert n_hours in (3, 4)

    # Our selection depends on the month and on the number of hours we want
    if month in ('06', '07'):
        top_n_regions = _apply_makeup_procedure(processed_regions, n_hours, month)
    elif month in ('08', '09', '10', '11', '12', '13'):
        if n_hours == 3:
            top_n_regions = _apply_makeup_procedure(processed_regions, n_hours, month)
        elif n_hours == 4:
            top_n_regions = _filter_listened_to_regions(processed_regions)
    elif month in ('14', '15', '16', '17'):
        if n_hours == 3:
            top_n_regions = _filter_listened_to_regions(processed_regions)
        elif n_hours == 4:
            return None
    else:
        raise ValueError(f'Unexpected month: {month}')

    kind = TOP_3_KIND if n_hours == 3 else TOP_4_KIND
    return top_n_regions.pipe(_standardize_regions, kind=kind)


def _make_complementary_intervals(intervals_df):
    """
    Makes intervals that are complementary to the given intervals. All the intervals are assumed to be finite - two of
    the complementary intervals will be infinite on one side, marked by an empty start/end.
    :param intervals_df: A dataframe with start and end columns corresponding to non-overlapping intervals
    :return: A dataframe with start and end columns corresponding to complementary intervals, the first start is empty,
    so is the last end. In case two of the input intervals are adjacent, the complementary interval will be zero-lenght
    but will still be present.
    """
    intervals_df = (intervals_df
                    # We are gonna introduce NAs next, so we want datatypes that support NAs without extra conversions
                    .convert_dtypes()
                    .sort_values(by=['start', 'end'])[['start', 'end']]
                    .reset_index(drop=True))
    # There is one more complementary region than there are regions - we'll prepare an empoty row for it.
    intervals_df.loc[max(intervals_df.index) + 1, :] = None
    # Complementary intervals go from the end of one interval to the start of the next one. Original starts already
    # correspond to the ends of the complementary intervals, so we'll just need to shift the original ends forward.
    intervals_df['new_end'] = intervals_df.start
    intervals_df['new_start'] = intervals_df.end.shift(1)
    complementary_df = intervals_df[['new_start', 'new_end']].rename(columns=lambda c: c.replace('new_', ''))

    return complementary_df.reset_index(drop=True)


def get_surplus_regions(processed_regions, month, duration_ms=None):
    """
    Given a dataframe with regions, return a dataframe with regions that belong to surplus hours. For months 8-17, these
    regions are explicitly marked as surplus. For months 6-7, we'll take the complement of their top 4 hours.
    """
    if month in ('06', '07'):
        assert duration_ms is not None

        # First approximation: surplus is everything but top 4 hours. This doesn't account for silence yet.
        surplus_regions_raw = (
            processed_regions
            .pipe(get_top_n_regions, month=month, n_hours=4)
            .pipe(_make_complementary_intervals)
            # We know the start of the first surplus region is 0, but we don't know the end of the last one
            .assign(start=lambda df: df.start.fillna(0),
                    end=lambda df: df.end.fillna(duration_ms),
                    region_type=RegionType.SURPLUS.value)
            # Remove zero-length intervals
            .loc[lambda df: df.end > df.start])

        # Add silence, remove overlaps, remove silences
        silence_regions = processed_regions.loc[lambda df: df.region_type == RegionType.SILENCE.value,
                                                surplus_regions_raw.columns]
        surplus_regions = (
            pd.concat([surplus_regions_raw, silence_regions], ignore_index=True)
            .pipe(_remove_overlaps_from_other_regions, dominant_region_type=RegionType.SILENCE.value)
            .loc[lambda df: df.region_type != RegionType.SILENCE.value]
            # # Replace pseudo-inf back with NA
            .assign(end=lambda df: _pseudo_inf_to_na(df.end))
        )
    elif 8 <= int(month) <= 17:
        surplus_regions = processed_regions.loc[lambda df: df.region_type == RegionType.SURPLUS.value]

    if surplus_regions.empty:
        return None
    else:
        return surplus_regions.pipe(_standardize_regions, kind=SURPLUS_KIND)


def get_top3_top4_surplus_regions(processed_regions, month, duration_ms):
    """
    Combine top 3, top 4, and surplus regions into a single dataframe.
    :param processed_regions:
    :param month: 6-17
    :param duration_ms: total duration of the recording - needed to fill in the end of the last surplus region for
    months 6-7
    :return: dataframe with columns kind, start, end
    """
    return pd.concat([
        get_top_n_regions(processed_regions, month, n_hours=3),
        get_top_n_regions(processed_regions, month, n_hours=4),
        get_surplus_regions(processed_regions, month, duration_ms)], ignore_index=True)


def _assign_tokens_to_regions(tokens, seedlings_nouns_regions, month):
    """
    Given a dataframe with tokens and a dataframe with top 3, top 4, and surplus regions, return a dataframe with
    columns annotid, is_top_3_hours, is_top_4_hours, is_surplus. Depending on the month, some of those can be NA instead
    of False.

    :param tokens: tokens to assign to top3/top4/surplus/subregion, annotid, onset columns are required
    :param seedlings_nouns_regions: top3/top4/surplus/subregion regions
    :param month: 6-17
    :return: a dataframe with annotid, is_top_3_hours, is_top_4_hours, is_surplus
    """
    # Find all annotids that are in top 3, top 4, or surplus regions. List them as (annotid, region_type) pairs.
    tokens_assigned_long = (
        tokens
        .rename(columns={'onset': 'onset_token'})
        # take all combinations of tokens and regions
        .merge(
            (seedlings_nouns_regions
             [['region_type', 'start', 'end', 'position', 'subregion_rank']]
             .rename(columns={'start': 'onset_region', 'end': 'offset_region'})),
            how='cross')
        # Keep only those combinations where the token is inside the region.
        .loc[lambda df: (df.onset_token >= df.onset_region) & ((df.onset_token < df.offset_region)
                                                               | df.offset_region.isna())]
        [['annotid', 'region_type', 'position', 'subregion_rank']]
        # Add back tokens that didn't match any region (there shouldn't be any)
        .pipe(lambda df: tokens[['annotid']].merge(df, how='left'))
    )
    assert not tokens_assigned_long.region_type.isnull().any()

    # Go wide - from (annotid, region_type) pairs to annotid, is_top_3_hours, is_top_4_hours, is_surplus
    tokens_assigned_pivot = (
        tokens_assigned_long
        .drop(columns=['position', 'subregion_rank'])
        .replace({TOP_3_KIND: 'is_top_3_hours',
                  TOP_4_KIND: 'is_top_4_hours',
                  SURPLUS_KIND: 'is_surplus',
                  RegionType.SUBREGION.value: 'is_subregion'})
        # We need a column with values to populate the pivot table. Values in the pivot table will be True iff the
        # (annotid, region_type) pair is present in the original dataframe.
        .assign(is_in=True)
        .pivot(index='annotid', columns=['region_type'])
        # all is_* columns are under the top level name "is_in" - we don't need it
        .droplevel(0, axis='columns')
        # Add back position and subregion_rank from the subregions
        .merge(tokens_assigned_long
               .loc[lambda df: df.region_type.eq(RegionType.SUBREGION.value),
                    ['annotid', 'position', 'subregion_rank']],
               on='annotid', how='left')
    )

    # For months 13-17, there are not top 4 regions, for some recordings in months 8-17, there are no surplus regions.
    if 14 <= int(month) <= 17:
        tokens_assigned_pivot['is_top_4_hours'] = pd.Series(None, dtype=pd.BooleanDtype())
    if 'is_surplus' not in tokens_assigned_pivot.columns:
        tokens_assigned_pivot['is_surplus'] = pd.Series(None, dtype=pd.BooleanDtype())

    # Clean it up: remove unnecessary index/column names levels, make annotid the column, etc.
    tokens_assigned_wide = (
        tokens_assigned_pivot
        # enforce the order of columns
        [['annotid', 'is_subregion', 'is_top_3_hours', 'is_top_4_hours', 'is_surplus', 'position', 'subregion_rank']]
        .sort_values(by='annotid')  # sort for consistency
        .convert_dtypes())  # convert to datatypes that support NAs

    # Substitute NAs with False, unless the month is 14-17 and the column is is_top_4_hours, then it all should be NA
    # because only three hours were annotated in months 14-17
    tokens_assigned_wide.is_top_3_hours = tokens_assigned_wide.is_top_3_hours.fillna(False)
    tokens_assigned_wide.is_subregion = tokens_assigned_wide.is_subregion.fillna(False)
    if 14 <= int(month) <= 17:
        assert tokens_assigned_wide.is_top_4_hours.isnull().all()
    else:
        tokens_assigned_wide.is_top_4_hours = tokens_assigned_wide.is_top_4_hours.fillna(False)
    tokens_assigned_wide.is_surplus = tokens_assigned_wide.is_surplus.fillna(False)

    return tokens_assigned_wide


def _check_tokens_assigned(tokens_assigned, tokens, month):
    """
    Runs some sanity checks on the tokens assigned to top3/top4/surplus regions.
    :param tokens: tokens to
    :param tokens_assigned:
    :return:
    """
    ta = tokens_assigned
    is_month_06_13 = 6 <= int(month) <= 13
    is_month_14_17 = 14 <= int(month) <= 17
    assert is_month_06_13 | is_month_14_17

    # is_surplus, is_top_3_hours should be not-null for all tokens, is_top_4_hours - for tokens from months 06-13 and
    # only fot them.
    assert ta[['is_surplus', 'is_top_3_hours']].notnull().all().all()
    assert ta.is_top_4_hours.notnull().all() == is_month_06_13
    assert ta.is_top_4_hours.isnull().all() == is_month_14_17

    # All top-3 tokens should also be top-4 tokens for months 06-13 (for months 14-17 top-4 is undefined)
    if is_month_06_13:
        assert not (ta.is_top_3_hours & ~ta.is_top_4_hours).any()

    # All tokens are either surplus or top-3/top-4 but not both
    assert not (ta.is_surplus & (ta.is_top_3_hours | ta.is_top_4_hours)).any()

    # All tokens are something
    assert not (ta.is_surplus | ta.is_top_3_hours | ta.is_top_4_hours).isna().any()

    # Tokens haven't changed
    assert set(ta.annotid.values) == set(tokens.annotid.values)


def assign_tokens_to_regions(tokens, seedlings_nouns_regions, month):
    tokens_assigned = _assign_tokens_to_regions(tokens, seedlings_nouns_regions, month)
    _check_tokens_assigned(tokens_assigned, tokens, month)
    return tokens_assigned


# =============================================================================
# Little helper functions for dealing with na values used as the right bound of right-open intervals, essentially
# infinity. We have them because at that point in code we didn't know the duration of month 06 and 07 recordings and
# so the last surplus region was left open on the right.


def _fillna_with_pseudo_inf(series: pd.Series):
    """
    Replaces NA values in a pandas numeric series with the maximum value that can be represented by the series dtype.
    :param series: a numeric pandas series
    :return: a copy with NA values replaced
    """
    return series.copy().fillna(_get_pseudo_infinity(series))


def _pseudo_inf_to_na(series: pd.Series):
    """
    If maximum possible values were used to represent infinity, replaces them with NA. Un
    :param series: a numeric pandas series
    :return: a copy with infinite values replaced with an appropriate NA value
    """
    try:
        na = series.dtype.na_value
    except (ValueError, AttributeError) as e:
        raise ValueError(f'The dtype of the series {series.dtype} does not support NA values') from e

    try:
        inf = _get_pseudo_infinity(series)
    except NotImplementedError as e:
        raise NotImplementedError(f"Can't get a pseudo-infinity for dtype {series.dtype}") from e

    return series.copy().replace(inf, na)


def _get_pseudo_infinity(series: pd.Series):
    """ Returns pseudo-infinity - the maximum value for the dtype of a pandas series. """
    try:
        pseudo_infinity = _numeric_dtype_info(numpy_dtype=series.dtype.numpy_dtype).max
    except NotImplementedError as e:
        raise NotImplementedError(f"Can't get a pseudo-infinity for dtype {series.dtype}") from e

    return pseudo_infinity


def _numeric_dtype_info(numpy_dtype):
    """
    Return the info object for a numpy dtype (see np.iinfo, np.finfo).
    :param numpy_dtype: numpy dtype
    :return: an object with attributes `min`, `max`, and `dtype` with the corresponding values for the given dtype.
    """
    if np.issubdtype(numpy_dtype, np.integer):
        info_fun = np.iinfo
    elif np.issubdtype(numpy_dtype, np.floating):
        info_fun = np.finfo
    else:
        raise NotImplementedError(f"I only know how to get max value for integer and float dtypes, not {numpy_dtype}")

    return info_fun(numpy_dtype)
