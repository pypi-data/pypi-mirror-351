"""
Module with the EafTree classes that represent EafFile contents as an xml.etree.ElementTree.ElementTree object with
convenient access to all the data. As much as possible, all the data is stored in the ElementTree object itself, so that
that object always represent the current state of data and can be written to disk at any time. Avoiding moving data from
xml representation to internal representation and then recreating xml representation when writing to disk as is done in
pympi.Eaf (and EafPlus) makes it easier to avoid inconsistencies and makes diffs between the input and the output .eaf
files to the minimum.

TODO:
[ ] Add superclasses/mixins:
    [ ] Add a superclass for Annotation and Tier - smth like EafElementWithRelations.
    [ ] Add a superclass for Annotation and ControlledVocabularyEntry - smth like EafElementWithInnerElements
[ ] Do not duplicate functionality from etree_utils, call those functions instead.
"""

import functools
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree as element_tree

import requests

from blabpy.eaf.etree_utils import element_to_string, _make_find_xpath, no_text_in_element


class EafElement(object):
    """
    Base class for all EAF elements.
    TODO:
    - move __init__() and validate() here,
    - define mandatory constants (TAG, ID, etc.),
    - define MandatoryAttribute, ConditionalAttribute, and OptionalAttribute classes,
    - move conditional_property() here,
    """
    @property
    def element(self):
        return self._element

    @property
    def id(self):
        return self.element.attrib[self.ID]

    def _validate_no_text(self):
        if not no_text_in_element(self.element):
            text = self.element.text
            raise ValueError(f'{self.TAG} element must not have text, had "{text.strip()}" instead.')

    def _validate_no_attributes(self):
        attributes = self.element.attrib
        if attributes:
            raise ValueError(f'{self.TAG} element must not have attributes, had "{attributes}" instead.')



def conditional_annotation_property(annotation_type):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self):
            if self.annotation_type != annotation_type:
                raise ValueError(f'Only {annotation_type}s have {func.__name__}.')
            return func(self)
        return property(wrapper)
    return decorator


class Annotation(EafElement):
    TAG = 'ANNOTATION'
    ID = 'ANNOTATION_ID'

    ALIGNABLE_ANNOTATION = 'ALIGNABLE_ANNOTATION'
    REF_ANNOTATION = 'REF_ANNOTATION'
    ANNOTATION_VALUE = 'ANNOTATION_VALUE'

    ANNOTATION_REF = 'ANNOTATION_REF'
    TIME_SLOT_REF1 = 'TIME_SLOT_REF1'
    TIME_SLOT_REF2 = 'TIME_SLOT_REF2'
    CVE_REF = 'CVE_REF'

    def __init__(self, annotation_element, eaf_tree, tier):
        # TODO: drop eaf_tree, return self.tier.eaf_tree in the eaf_tree property
        self._element = annotation_element
        self._eaf_tree = eaf_tree
        self.tier = tier
        self.validate()
        self._children = None

    def __repr__(self):
        return f'<{self.annotation_type} {self.id} from tier {self.tier.id}:  {self.value}>'

    @property
    def eaf_tree(self):
        return self._eaf_tree

    @property
    def inner_element(self):
        return self.element[0]

    @property
    def value_element(self):
        return self.inner_element[0]

    @property
    def value(self):
        return self.value_element.text

    def clear_value(self):
        self.value_element.text = ''

    def value_not_set(self):
        return no_text_in_element(self.value_element)

    @value.setter
    def value(self, value):
        if self.tier.uses_cv:
            cv = self.tier.cv
            cve_ref = cv.get_id_of_value(value)
            self.inner_element.attrib[self.CVE_REF] = cve_ref
        self.value_element.text = value

    @property
    def id(self):
        return self.inner_element.attrib[self.ID]

    @property
    def annotation_type(self):
        return self.inner_element.tag

    @conditional_annotation_property(ALIGNABLE_ANNOTATION)
    def time_slot_ref1(self):
        return self.inner_element.attrib[self.TIME_SLOT_REF1]

    @conditional_annotation_property(ALIGNABLE_ANNOTATION)
    def time_slot_ref2(self):
        return self.inner_element.attrib[self.TIME_SLOT_REF2]

    @conditional_annotation_property(REF_ANNOTATION)
    def annotation_ref(self):
        return self.inner_element.attrib[self.ANNOTATION_REF]

    @conditional_annotation_property(REF_ANNOTATION)
    def parent(self):
        return self.eaf_tree.annotations[self.annotation_ref]

    @property
    def children(self):
        # Should be a list, possibly an empty one
        if self._children is None:
            raise ValueError(f'The children tiers have not been assigned, tell lab technician.')
        return self._children

    @property
    def children_assigned(self):
        return self._children is not None

    def mark_as_childless(self):
        if self._children is not None:
            if len(self._children) > 0:
                raise ValueError(f'Can\'t mark annotation {self.id} as childless because it has children.')
            else:
                raise ValueError(f'Annotation {self.id} has already been marked as childless.')
        self._children = []

    def _set_time_slot_value(self, time_slot_ref_attr_name, value_ms):
        if not isinstance(value_ms, int):
            raise TypeError(f"Time slot value must be an integer, got {type(value_ms)}")
        time_slot_id = self.inner_element.attrib[time_slot_ref_attr_name]
        time_slot = self.eaf_tree.time_slots[time_slot_id]
        time_slot.element.attrib[TimeSlot.TIME_VALUE] = str(value_ms)

    def _time_slot_setter(self, slot_type: str, value_ms: int):
        """Helper method to set onset or offset time slot values."""
        if self.annotation_type != self.ALIGNABLE_ANNOTATION:
            raise ValueError(f"Cannot set {slot_type} for a non-alignable annotation.")

        if slot_type == "onset":
            slot_ref_attr = self.TIME_SLOT_REF1
        elif slot_type == "offset":
            slot_ref_attr = self.TIME_SLOT_REF2
        else:
            raise ValueError(f"Invalid slot_type '{slot_type}'. Must be 'onset' or 'offset'.")

        self._set_time_slot_value(slot_ref_attr, value_ms)

    @property
    def onset(self):
        if self.annotation_type == self.ALIGNABLE_ANNOTATION:
            return int(self.eaf_tree.time_slots[self.time_slot_ref1].time_value)
        else:
            return self.parent.onset

    @onset.setter
    def onset(self, value_ms):
        self._time_slot_setter("onset", value_ms)

    @property
    def offset(self):
        if self.annotation_type == self.ALIGNABLE_ANNOTATION:
            return int(self.eaf_tree.time_slots[self.time_slot_ref2].time_value)
        else:
            return self.parent.offset

    @offset.setter
    def offset(self, value_ms):
        self._time_slot_setter("offset", value_ms)

    def append_child(self, child):
        self._children = self._children or list()
        self._children.append(child)

    def gather_descendants(self):
        """
        Gather all descendants of this annotation as a list of Annotation objects.
        :return: a list of annotations
        """
        descendants = list()
        for child in self.children:
            descendants.extend([child] + child.gather_descendants())
        return descendants

    @conditional_annotation_property(REF_ANNOTATION)
    def cve_ref(self):
        return self.inner_element.attrib[self.CVE_REF]

    @cve_ref.setter
    def cve_ref(self, cve_ref):
        self.inner_element.attrib[self.CVE_REF] = cve_ref

    def validate(self):
        """
        Check that the annotation element either looks like this:

        <ANNOTATION>
            <ALIGNABLE_ANNOTATION ANNOTATION_ID="a62" TIME_SLOT_REF1="ts14" TIME_SLOT_REF2="ts15">
                <ANNOTATION_VALUE>hi.</ANNOTATION_VALUE>
            </ALIGNABLE_ANNOTATION>
        </ANNOTATION>

        or like this:

        <ANNOTATION>
            <REF_ANNOTATION ANNOTATION_ID="a926" ANNOTATION_REF="a146" CVE_REF="cveid0">
                <ANNOTATION_VALUE>C</ANNOTATION_VALUE>
            </REF_ANNOTATION>
        </ANNOTATION>

        With the CVE_REF attribute being there iff the tier uses a controlled vocabulary.
        """
        # Validate outer element
        if self.element.tag != self.TAG:
            raise ValueError(f'Annotation element must have {self.TAG} as its tag.')
        if len(self.element) != 1:
            raise ValueError(f'Annotation element must have exactly one child element.')
        self._validate_no_attributes()
        self._validate_no_text()

        # Validate inner element
        inner_element = self.inner_element
        if len(inner_element) != 1:
            raise ValueError(f'Inner annotation element must have exactly one child element.')
        if inner_element.text and not inner_element.text.isspace():
            raise ValueError(f'Inner annotation element must not have text.')

        attribute_names = set(inner_element.attrib.keys())
        if inner_element.tag == self.ALIGNABLE_ANNOTATION:
            if attribute_names != {'ANNOTATION_ID', 'TIME_SLOT_REF1', 'TIME_SLOT_REF2'}:
                raise ValueError(f'ALIGNABLE_ANNOTATION must have {self.ID}, {self.TIME_SLOT_REF1},'
                                 f' and {self.TIME_SLOT_REF2} attributes.')
        elif inner_element.tag == self.REF_ANNOTATION:
            necessary_attributes = {'ANNOTATION_ID', 'ANNOTATION_REF'}
            conditional_attributes = {'CVE_REF'}
            if not necessary_attributes.issubset(attribute_names):
                raise ValueError(f'REF_ANNOTATION must have {self.ID} and {self.ANNOTATION_REF} attributes.')
            if not attribute_names.issubset(necessary_attributes.union(conditional_attributes)):
                raise ValueError(f'REF_ANNOTATION must not have any other attributes than {necessary_attributes} and '
                                 f'{conditional_attributes}.')
        else:
            raise ValueError(f'Unknown annotation type: {inner_element.tag}')

        value_element = self.value_element
        if value_element.tag != self.ANNOTATION_VALUE:
            raise ValueError(f'Inner annotation element must have {self.ANNOTATION_VALUE} as its child element.')
        if value_element.attrib:
            raise ValueError(f'Inner annotation element must not have attributes.')

        # For tiers with controlled vocabularies, check that CVE_REF and annotation value are both present and
        # consistent or both absent.
        if self.eaf_tree.validate_cv_entries and self.annotation_type == self.REF_ANNOTATION and self.tier.uses_cv:
            not_empty = not self.value_not_set()
            cve_ref = self.inner_element.attrib.get(self.CVE_REF)
            has_cve_ref = cve_ref is not None

            if has_cve_ref != not_empty:
                raise ValueError(f'For tiers with controlled vocabularies, {self.CVE_REF} attribute must be present iff '
                                 f'there is a non-empty value.')

            if has_cve_ref and cve_ref not in self.tier.cv.entries:
                raise ValueError(f'The annotation uses an invalid reference to a CV entry: {cve_ref}. This can happen\n'
                                 'if you switched to an external CV file which uses different cve_id\'s. If this is\n'
                                 'indeed the reason, you can run the following to update the references:\n'
                                 '\n'
                                 'eaf_tree = EafTree.from_eaf(eaf_path, validate_cv_entries=False)\n'
                                 'eaf_tree.update_cve_refs()\n')

            if not_empty and (self.value != self.tier.cv.entries[cve_ref].value):
                raise ValueError(f'Value {self.value} does not match the {cve_ref} item in the controlled vocabulary.')

    def update_cve_ref(self):
        """
        Used when the controlled vocabulary definitions have been moved to an external .ecv file and the cve_id's of
        the entries have been updated. Even if they haven't been updated, they will only match one file, so you might
        have to do it anyway.
        :return: None
        """
        if not self.value:
            return

        if not self.tier.uses_cv:
            raise ValueError(f'Tier {self.tier.id} does not use a controlled vocabulary.')

        try:
            cve_ref_for_value = self.tier.cv.get_id_of_value(self.value)
        except ValueError:
            raise ValueError(f'Value {self.value} is not in the controlled vocabulary.')

        self.cve_ref = cve_ref_for_value


class AlignableAnnotation(Annotation):
    @classmethod
    def make_xml_element(cls, annotation_id, time_slot_ref1, time_slot_ref2):
        # <ANNOTATION>
        #     <ALIGNABLE_ANNOTATION ANNOTATION_ID="a62" TIME_SLOT_REF1="ts14" TIME_SLOT_REF2="ts15">
        #         <ANNOTATION_VALUE>hi.</ANNOTATION_VALUE>
        #     </ALIGNABLE_ANNOTATION>
        # </ANNOTATION>
        element = element_tree.Element(cls.TAG)

        attributes = {cls.ID: annotation_id, cls.TIME_SLOT_REF1: time_slot_ref1, cls.TIME_SLOT_REF2: time_slot_ref2}
        inner_element = element_tree.Element(cls.ALIGNABLE_ANNOTATION, attrib=attributes)
        element.append(inner_element)

        annotation_value = element_tree.Element(cls.ANNOTATION_VALUE)
        inner_element.append(annotation_value)

        return element


class ReferenceAnnotation(Annotation):
    @classmethod
    def make_xml_element(cls, annotation_id, annotation_ref):
        # <ANNOTATION>
        #     <REF_ANNOTATION ANNOTATION_ID="a127" ANNOTATION_REF="a62" CVE_REF="cveid0">
        #         <ANNOTATION_VALUE>C</ANNOTATION_VALUE>
        #     </REF_ANNOTATION>
        # </ANNOTATION>
        element = element_tree.Element(cls.TAG)

        attributes = {cls.ID: annotation_id, cls.ANNOTATION_REF: annotation_ref}
        inner_element = element_tree.Element(cls.REF_ANNOTATION, attrib=attributes)
        element.append(inner_element)

        annotation_value = element_tree.Element(cls.ANNOTATION_VALUE)
        inner_element.append(annotation_value)

        return element


class Tier(EafElement):
    TAG = 'TIER'
    ID = 'TIER_ID'
    LINGUISTIC_TYPE_REF = 'LINGUISTIC_TYPE_REF'
    PARENT_REF = 'PARENT_REF'
    PARTICIPANT = 'PARTICIPANT'

    def __init__(self, tier_element, eaf_tree):
        self._element = tier_element
        self._eaf_tree = eaf_tree
        annotations = [Annotation(annotation_element, eaf_tree=eaf_tree, tier=self)
                       for annotation_element in tier_element]
        self.annotations = {annotation.id: annotation for annotation in annotations}
        self._children = None

    def __repr__(self):
        return f'<Tier {self.id} {self.linguistic_type_ref} {self.participant}>'

    @classmethod
    def make_xml_element(cls, tier_id, linguistic_type_ref, participant, parent_ref):
        attributes = {cls.ID: tier_id, cls.LINGUISTIC_TYPE_REF: linguistic_type_ref}
        if participant is not None:
            attributes[cls.PARTICIPANT] = participant
        if parent_ref is not None:
            attributes[cls.PARENT_REF] = parent_ref
        return element_tree.Element(cls.TAG, attrib=attributes)

    @property
    def eaf_tree(self):
        return self._eaf_tree

    @property
    def linguistic_type_ref(self):
        return self.element.attrib[self.LINGUISTIC_TYPE_REF]

    @property
    def linguistic_type(self):
        return self.eaf_tree.linguistic_types[self.linguistic_type_ref]

    @property
    def parent_ref(self):
        return self.element.attrib.get(self.PARENT_REF)

    @property
    def parent(self):
        if self.parent_ref is None:
            raise ValueError(f'Tier {self.id} doesn\'t have a parent.')
        return self.eaf_tree.tiers[self.parent_ref]

    @property
    def children(self):
        # Should be a list, possibly an empty one
        if self._children is None:
            raise ValueError(f'The parent tier has not been loaded, tell lab technician.')
        return self._children

    @property
    def children_assigned(self):
        return self._children is not None

    def mark_as_childless(self):
        if self._children is not None:
            if len(self._children) > 0:
                raise ValueError(f'Can\'t mark tier {self.id} as childless because it has children.')
            else:
                raise ValueError(f'Tier {self.id} has already been marked as childless.')
        self._children = []

    def append_child(self, child):
        self._children = self._children or list()
        self._children.append(child)

    def gather_descendants(self):
        """
        Gather all descendants of this annotation as a list of Tier objects.
        :return: a list of annotations
        """
        descendants = list()
        for child in self.children:
            descendants.extend([child] + child.gather_descendants())
        return descendants

    @property
    def participant(self):
        return self.element.attrib.get(self.PARTICIPANT)

    @property
    def uses_cv(self):
        return self.linguistic_type.uses_cv

    @property
    def cv(self):
        return self.linguistic_type.cv

    def validate(self):
        if self.element.tag != self.TAG:
            raise ValueError(f'Tier element must have {self.TAG} as its tag.')
        necessary_attributes = {self.LINGUISTIC_TYPE_REF, self.ID}
        possible_extra_attributes = {self.PARENT_REF, self.PARTICIPANT}
        attribute_names = set(self.element.attrib.keys())
        if not necessary_attributes.issubset(attribute_names):
            raise ValueError(f'Tier element must have {self.LINGUISTIC_TYPE_REF} and {self.ID} attributes.')
        if not attribute_names.issubset(necessary_attributes.union(possible_extra_attributes)):
            raise ValueError(f'Tier element must not have any other attributes than {necessary_attributes} and '
                             f'{possible_extra_attributes}.')
        self._validate_no_text()

    def _add_annotation(self, annotation_xml_element):
        """
        Helper method to add an annotation to the tier.

        Args:
            annotation_xml_element: The XML element for the annotation

        Returns:
            The added Annotation instance
        """
        added_annotation = Annotation(annotation_xml_element, eaf_tree=self.eaf_tree, tier=self)
        self.element.append(added_annotation.element)
        self.annotations[added_annotation.id] = added_annotation
        self.eaf_tree.annotations[added_annotation.id] = added_annotation
        return added_annotation

    def _add_alignable_annotation(self, annotation_id, time_slot_ref1, time_slot_ref2):
        """
        Private method to add an alignable annotation to the tier with explicit annotation_id and prepared time slots.

        Args:
            annotation_id: The ID of the annotation
            time_slot_ref1: The ID of the first time slot
            time_slot_ref2: The ID of the second time slot

        Returns:
            The added Annotation instance
        """
        annotation_xml_element = AlignableAnnotation.make_xml_element(
            annotation_id=annotation_id,
            time_slot_ref1=time_slot_ref1,
            time_slot_ref2=time_slot_ref2)

        return self._add_annotation(annotation_xml_element)

    def _add_reference_annotation(self, annotation_id, parent_annotation_id):
        """
        Private method to add a reference annotation to the tier with explicit annotation_id.

        Args:
            annotation_id: The ID of the annotation
            parent_annotation_id: The ID of the parent annotation

        Returns:
            The added Annotation instance
        """
        annotation_xml_element = ReferenceAnnotation.make_xml_element(
            annotation_id=annotation_id,
            annotation_ref=parent_annotation_id)

        return self._add_annotation(annotation_xml_element)

    def _generate_annotation_id(self):
        """
        Generate a new annotation ID and update the last used ID counter.

        Returns:
            The new annotation ID string
        """
        last_used_annotation_id = self.eaf_tree.last_used_annotation_id + 1
        annotation_id = f'a{last_used_annotation_id}'
        # Update the last used annotation ID
        self.eaf_tree.last_used_annotation_id = last_used_annotation_id
        return annotation_id

    def add_alignable_annotation(self, onset_ms, offset_ms, value=None, annotation_id=None):
        """
        Add an alignable annotation to the tier.

        Args:
            onset_ms: Onset time in milliseconds
            offset_ms: Offset time in milliseconds
            value: Optional initial value for the annotation
            annotation_id: Optional specific ID to use (default: auto-generate)

        If you specify annotation_id, the function won't update the last used annotation id in the eaf_tree - it is on
        the user.

        Returns:
            The added Annotation instance
        """
        # Generate a new annotation ID if not provided
        if annotation_id is None:
            annotation_id = self._generate_annotation_id()

        # Create new time slots
        time_slot_ref1 = self.eaf_tree.create_time_slot(onset_ms)
        time_slot_ref2 = self.eaf_tree.create_time_slot(offset_ms)

        # Add the annotation
        annotation = self._add_alignable_annotation(annotation_id, time_slot_ref1, time_slot_ref2)

        # Set value if provided
        if value is not None:
            annotation.value = value

        return annotation

    def add_reference_annotation(self, parent_annotation_id, value=None, annotation_id=None):
        """
        Add a reference annotation to the tier.

        Args:
            parent_annotation_id: The ID of the parent annotation
            value: Optional initial value for the annotation
            annotation_id: Optional specific ID to use (default: auto-generate)

        If you specify annotation_id, the function won't update the last used annotation id in the eaf_tree - it is on
        the user.

        Returns:
            The added Annotation instance
        """
        # Generate a new annotation ID if not provided
        if annotation_id is None:
            annotation_id = self._generate_annotation_id()

        # Add the annotation
        annotation = self._add_reference_annotation(annotation_id, parent_annotation_id)

        # Set value if provided
        if value is not None:
            annotation.value = value

        # Add as child to parent annotation
        parent_annotation = self.eaf_tree.annotations[parent_annotation_id]
        parent_annotation.append_child(annotation)

        return annotation

    def drop_annotation(self, annotation_id):
        if annotation_id not in self.annotations:
            raise ValueError(f'Annotation {annotation_id} not found in tier {self.id}.')

        annotation = self.annotations[annotation_id]

        if len(annotation.children) > 0:
            raise ValueError(f'Annotation {annotation_id} has child annotations and cannot be dropped.')

        if annotation.annotation_type == Annotation.REF_ANNOTATION:
            annotation.parent.children.remove(annotation)
        del self.annotations[annotation_id]
        del self.eaf_tree.annotations[annotation_id]
        self.element.remove(annotation.element)

    def drop_all_annotations(self):
        for annotation_id in list(self.annotations.keys()):
            self.drop_annotation(annotation_id)


class LinguisticType(EafElement):
    TAG = 'LINGUISTIC_TYPE'
    ID = 'LINGUISTIC_TYPE_ID'
    TIME_ALIGNABLE = 'TIME_ALIGNABLE'
    GRAPHIC_REFERENCES = 'GRAPHIC_REFERENCES'
    NECESSARY_ATTRIBUTES = {ID, TIME_ALIGNABLE, GRAPHIC_REFERENCES}

    CONSTRAINTS = 'CONSTRAINTS'
    CONTROLLED_VOCABULARY_REF = 'CONTROLLED_VOCABULARY_REF'
    POSSIBLE_EXTRA_ATTRIBUTES = {CONSTRAINTS, CONTROLLED_VOCABULARY_REF}

    def __init__(self, linguistic_type_element, eaf_tree):
        self._element = linguistic_type_element
        self._eaf_tree = eaf_tree
        self.validate()

    @property
    def eaf_tree(self):
        return self._eaf_tree

    @property
    def time_alignable(self):
        return self.element.attrib[self.TIME_ALIGNABLE]

    @property
    def graphic_references(self):
        return self.element.attrib[self.GRAPHIC_REFERENCES]

    @property
    def constraints(self):
        return self.element.attrib.get(self.CONSTRAINTS)

    @property
    def controlled_vocabulary_ref(self):
        return self.element.attrib.get(self.CONTROLLED_VOCABULARY_REF)

    @property
    def uses_cv(self):
        return self.controlled_vocabulary_ref is not None

    @property
    def cv(self):
        if not self.uses_cv:
            raise ValueError(f'This linguistic type does not use a controlled vocabulary.')
        else:
            return self.eaf_tree.controlled_vocabularies[self.controlled_vocabulary_ref]

    def validate(self):
        if self.element.tag != self.TAG:
            raise ValueError(f'LinguisticType element must have {self.TAG} as its tag.')
        attribute_names = set(self.element.attrib.keys())
        if not self.NECESSARY_ATTRIBUTES.issubset(attribute_names):
            raise ValueError(f'LinguisticType element must have {self.NECESSARY_ATTRIBUTES} attributes.')
        if not attribute_names.issubset(self.NECESSARY_ATTRIBUTES.union(self.POSSIBLE_EXTRA_ATTRIBUTES)):
            raise ValueError(f'LinguisticType element must not have any other attributes than {self.NECESSARY_ATTRIBUTES} '
                             f'and {self.POSSIBLE_EXTRA_ATTRIBUTES}.')
        self._validate_no_text()

    @classmethod
    def make_xml_element(cls, linguistic_type_id, time_alignable: bool, graphic_references: bool,
                         constraints_ref=None, cv_ref=None):
        attributes = {
            cls.ID: linguistic_type_id,
            cls.TIME_ALIGNABLE: str(time_alignable).lower(),
            cls.GRAPHIC_REFERENCES: str(graphic_references).lower()
        }
        if constraints_ref:
            attributes[cls.CONSTRAINTS] = constraints_ref
        if cv_ref:
            attributes[cls.CONTROLLED_VOCABULARY_REF] = cv_ref
        return element_tree.Element(cls.TAG, attrib=attributes)


class ControlledVocabularyEntry(EafElement):
    TAG = 'CV_ENTRY_ML'
    ID = 'CVE_ID'
    CVE_VALUE = 'CVE_VALUE'
    ALL_ATTRIBUTES = {ID}

    def __init__(self, cv_entry_element):
        """
        <CV_ENTRY_ML CVE_ID="cveid0">
            <CVE_VALUE DESCRIPTION="Present" LANG_REF="und">P</CVE_VALUE>
        </CV_ENTRY_ML>
        """
        self._element = cv_entry_element
        self.validate()

    @property
    def value_element(self):
        return self._element[0]

    @property
    def description(self):
        return self.value_element.attrib['DESCRIPTION']

    @property
    def value(self):
        return self.value_element.text

    def validate(self):
        if self.element.tag != self.TAG:
            raise ValueError(f'Controlled vocabulary entry element must have {self.TAG} as its tag.')
        attribute_names = set(self.element.attrib.keys())
        if self.ALL_ATTRIBUTES != attribute_names:
            raise ValueError(f'Controlled vocabulary entry element must have {self.ALL_ATTRIBUTES} attributes and only'
                             f' them.')

        (self._value_element, ) = self.element
        if self._value_element.tag != self.CVE_VALUE:
            raise ValueError(f'Controlled vocabulary entry element must have {self.CVE_VALUE} as its child element.')
        if self._value_element.attrib.keys() != {'DESCRIPTION', 'LANG_REF'}:
            raise ValueError(f'Controlled vocabulary entry element must have DESCRIPTION and LANG_REF attributes.')
        if not self._value_element.text:
            raise ValueError(f'Controlled vocabulary entry element must have text.')

    @classmethod
    def make_xml_element(cls, cve_id, description, value, lang_ref="und"):
        """
        Creates an XML element for a CV_ENTRY_ML.
        <CV_ENTRY_ML CVE_ID="cveid0">
            <CVE_VALUE DESCRIPTION="Present" LANG_REF="und">P</CVE_VALUE>
        </CV_ENTRY_ML>
        """
        cv_entry_ml_element = element_tree.Element(cls.TAG, attrib={cls.ID: cve_id})
        cve_value_element = element_tree.Element(
            cls.CVE_VALUE,
            attrib={'DESCRIPTION': description, 'LANG_REF': lang_ref}
        )
        cve_value_element.text = value
        cv_entry_ml_element.append(cve_value_element)
        return cv_entry_ml_element


class ControlledVocabulary(EafElement):
    TAG = 'CONTROLLED_VOCABULARY'
    ID = 'CV_ID'
    DESCRIPTION = 'DESCRIPTION'
    EXT_REF = 'EXT_REF'
    # TODO: it isn't necessary to have EXT_REF, the CV can be defined in the element itself. Allow for that.
    NECESSARY_ATTRIBUTES = {ID}
    POSSIBLE_EXTRA_ATTRIBUTES = {EXT_REF}

    def __init__(self, cv_element, eaf_tree):
        self._element = cv_element
        self._eaf_tree = eaf_tree
        self.validate()
        if not self.ext_ref:
            self._description, self._entries = self.parse()

    @property
    def eaf_tree(self):
        return self._eaf_tree

    @property
    def ext_ref(self):
        return self.element.get(self.EXT_REF)

    @property
    def external_reference(self):
        if self.ext_ref:
            return self.eaf_tree.external_references[self.ext_ref]
        else:
            raise ValueError(f'This controlled vocabulary does not have an external reference.')

    @property
    def external_cv(self):
        return self.external_reference.cv_resource.cvs[self.id]

    @property
    def description(self):
        if self.ext_ref:
            return self.external_cv.description
        else:
            return self._description

    @property
    def entries(self):
        if self.ext_ref:
            return self.external_cv.entries
        else:
            return self._entries

    def get_id_of_value(self, value):
        try:
            (cve_id,) = {cve_id for cve_id, cv_entry in self.entries.items() if cv_entry.value == value}
        except ValueError:
            raise ValueError(f'Value {value} is not in the controlled vocabulary.')
        return cve_id

    def validate(self):
        if self.element.tag != self.TAG:
            raise ValueError(f'Controlled vocabulary element must have {self.TAG} as its tag.')
        attribute_names = set(self.element.attrib.keys())
        if not self.NECESSARY_ATTRIBUTES.issubset(attribute_names):
            raise ValueError(f'Controlled vocabulary element must have {self.NECESSARY_ATTRIBUTES} attributes.')
        if not attribute_names.issubset(self.NECESSARY_ATTRIBUTES.union(self.POSSIBLE_EXTRA_ATTRIBUTES)):
            raise ValueError(f'Controlled vocabulary element must not have any other attributes than '
                             f'{self.NECESSARY_ATTRIBUTES} and {self.POSSIBLE_EXTRA_ATTRIBUTES}.')
        self._validate_no_text()

    def parse(self):
        """
        <CONTROLLED_VOCABULARY CV_ID="present">
            <DESCRIPTION LANG_REF="und">generalized flag</DESCRIPTION>
            <CV_ENTRY_ML CVE_ID="cveid0">
                <CVE_VALUE DESCRIPTION="Present" LANG_REF="und">P</CVE_VALUE>
            </CV_ENTRY_ML>
        </CONTROLLED_VOCABULARY>
        """
        (description_element, ) = [el for el in self.element if el.tag == self.DESCRIPTION]
        entry_elements = [ControlledVocabularyEntry(el)
                          for el in self.element if el.tag == ControlledVocabularyEntry.TAG]
        return description_element, {entry.id: entry for entry in entry_elements}

    @classmethod
    def make_xml_element(cls, cv_id, description_text=None, ext_ref_id=None, entries=None, lang_ref="und"):
        """
        Creates an XML element for a CONTROLLED_VOCABULARY.
        If ext_ref_id is provided, description_text and entries are ignored.
        entries should be a list of dicts: [{'cve_id': 'id', 'description': 'desc', 'value': 'val'}]
        """
        attributes = {cls.ID: cv_id}
        if ext_ref_id:
            attributes[cls.EXT_REF] = ext_ref_id
            return element_tree.Element(cls.TAG, attrib=attributes)
        
        # Internal CV definition
        cv_element = element_tree.Element(cls.TAG, attrib=attributes)
        if description_text is not None:
            desc_element = element_tree.Element(cls.DESCRIPTION, attrib={'LANG_REF': lang_ref})
            desc_element.text = description_text
            cv_element.append(desc_element)
        
        if entries:
            for entry_data in entries:
                cve_element = ControlledVocabularyEntry.make_xml_element(
                    cve_id=entry_data['cve_id'],
                    description=entry_data['description'],
                    value=entry_data['value'],
                    lang_ref=lang_ref # Assuming same lang_ref for all entries for simplicity
                )
                cv_element.append(cve_element)
        return cv_element


class ExternalReference(EafElement):
    TAG = 'EXTERNAL_REF'
    ID = 'EXT_REF_ID'
    TYPE = 'TYPE'
    VALUE = 'VALUE'
    NECESSARY_ATTRIBUTES = {ID, TYPE, VALUE}

    def __init__(self, ext_ref_element):
        self._element = ext_ref_element
        self.validate()
        self.cv_resource = self.parse()

    def __repr__(self):
        return f'<ExternalReference {self.ext_ref_id} {self.type} {self.value}>'

    @property
    def ext_ref_id(self):
        return self.element.attrib[self.ID]

    @property
    def type(self):
        return self.element.attrib[self.TYPE]

    @property
    def value(self):
        return self.element.attrib[self.VALUE]

    def validate(self):
        if self.element.tag != self.TAG:
            raise ValueError(f'External reference element must have {self.TAG} as its tag.')
        attribute_names = set(self.element.attrib.keys())
        if not self.NECESSARY_ATTRIBUTES.issubset(attribute_names):
            raise ValueError(f'External reference element must have {self.NECESSARY_ATTRIBUTES} '
                             f'attributes.')
        self._validate_no_text()

    def parse(self):
        return ControlledVocabularyResource.from_uri(self.value)

    @classmethod
    def make_xml_element(cls, ext_ref_id, type_val, value_val):
        attributes = {
            cls.ID: ext_ref_id,
            cls.TYPE: type_val,
            cls.VALUE: value_val
        }
        return element_tree.Element(cls.TAG, attrib=attributes)


class XMLTree(object):
    def __init__(self, tree):
        self._tree = tree

    @property
    def tree(self):
        return self._tree

    @classmethod
    def from_path(cls, path, *args, **kwargs):
        with Path(path).open('r') as f:
            return cls(element_tree.parse(f), *args, **kwargs)

    @classmethod
    def from_url(cls, url, *args, **kwargs):
        u = requests.get(url)
        with StringIO() as f:
            f.write(u.content.decode())
            f.seek(0)
            tree = element_tree.parse(f)
        return cls(tree, *args, **kwargs)

    @classmethod
    def from_uri(cls, uri, *args, **kwargs):
        uri = str(uri)
        # TODO: parse the uri with urlparse instead of using startswith
        if uri.startswith('http'):
            return cls.from_url(uri, *args, **kwargs)
        else:
            path = uri.replace('file:', '')
            return cls.from_path(path, *args, **kwargs)

    def to_string(self):
        return element_to_string(self.tree.getroot(), children=True)

    def to_file(self, path):
        Path(path).write_text(self.to_string(), newline='\n')

    @staticmethod
    def _make_find_xpath(tag, **attributes):
        if attributes:
            attribute_filters = [f'@{name}="{value}"' for name, value in attributes.items()]
            attributes_filter = '[' + ' and '.join(attribute_filters) + ']'
        else:
            attributes_filter = ''
        return f'.//{tag}{attributes_filter}'

    def find_element(self, tag, **attributes):
        return self.tree.find(_make_find_xpath(tag, **attributes))

    def find_elements(self, tag, **attributes):
        return self.tree.findall(_make_find_xpath(tag, **attributes))

    def find_single_element(self, tag, **attributes):
        """
        Find a single element in the tree. Raise an error if there are none or more than one.
        """
        elements = self.find_elements(tag, **attributes)
        if len(elements) == 0:
            raise ValueError(f'Couldn\'t find any elements with tag "{tag}" and attributes {attributes}.')
        elif len(elements) == 1:
            return elements[0]
        else:
            raise ValueError(f'Found more than one element with tag "{tag}" and attributes {attributes}.')

    def find_parent(self, element):
        for parent in self.tree.getroot().iter():
            for child in parent:
                if child is element:
                    return parent
        raise ValueError(f'Element {element} is not in the tree.')


class ControlledVocabularyResource(XMLTree):
    """
    An XML tree representation of a controlled vocabulary resource.
    """
    TAG = 'CV_RESOURCE'

    def __init__(self, cv_resource_tree):
        super().__init__(cv_resource_tree)
        cvs = [ControlledVocabulary(cv_element, eaf_tree=None)
               for cv_element in self.tree.getroot()
               if cv_element.tag == ControlledVocabulary.TAG]
        self._cvs = {cv.id: cv for cv in cvs}
        # TODO: add a class for languages
        self._language = self.find_single_element('LANGUAGE')
        # TODO: validate including xml schemas and such

    @property
    def cvs(self):
        return self._cvs

    @property
    def language(self):
        return self._language


class TimeSlot(EafElement):
    """
    <TIME_ORDER>
        <TIME_SLOT TIME_SLOT_ID="ts1" TIME_VALUE="3060000"></TIME_SLOT>
    """
    TAG = 'TIME_SLOT'
    ID = 'TIME_SLOT_ID'
    TIME_VALUE = 'TIME_VALUE'

    def __init__(self, time_slot_element, eaf_tree):
        self._element = time_slot_element

    @property
    def time_value(self):
        return self.element.attrib[self.TIME_VALUE]

    def __str__(self):
        return f'TimeSlot {self.id} at {self.time_value} ms'


class EafTree(XMLTree):
    """An XML tree representation of an EAF file."""
    EAF_ELEMENT_ORDER = (
        'HEADER', 'TIME_ORDER', Tier.TAG, LinguisticType.TAG, 'CONSTRAINT', 
        ControlledVocabulary.TAG, ExternalReference.TAG
    )

    @classmethod
    def from_eaf(cls, eaf_uri: str, *args, **kwargs):
        return cls.from_uri(eaf_uri, *args, **kwargs)

    def __init__(self, tree, validate_cv_entries=True):
        super().__init__(tree)
        self.validate_cv_entries = validate_cv_entries

        self.external_references = self._parse_elements(ExternalReference)
        self.controlled_vocabularies = self._parse_elements(ControlledVocabulary, eaf_tree=self)
        self.linguistic_types = self._parse_elements(LinguisticType, eaf_tree=self)
        self.tiers = self._parse_elements(Tier, eaf_tree=self)
        self.annotations = {id_: annotation
                            for tier in self.tiers.values()
                            for id_, annotation in tier.annotations.items()}
        self.time_slots = self._parse_elements(TimeSlot, eaf_tree=self)

        self.assign_children()

    def _parse_elements(self, element_class, *args, **kwargs):
        elements = [element_class(element, *args, **kwargs) for element in self.find_elements(element_class.TAG)]
        return {element.id: element for element in elements}

    @property
    def last_used_annotation_id_element(self):
        # Directly return the found element or raise
        found = self.find_element('PROPERTY', **dict(NAME='lastUsedAnnotationId'))
        if found is None:
            raise ValueError("PROPERTY tag with NAME='lastUsedAnnotationId' not found in EAF file.")
        return found

    @property
    def last_used_annotation_id(self) -> int:
        # Use the property element directly
        prop_val = self.last_used_annotation_id_element.text
        prop_val_int = int(prop_val) if prop_val and prop_val.isdigit() else 0
        max_id = max((int(annotation_id[1:]) for annotation_id in self.annotations), default=0)
        if prop_val_int < max_id:
            self.last_used_annotation_id_element.text = str(max_id)
            return max_id
        else:
            return prop_val_int

    @last_used_annotation_id.setter
    def last_used_annotation_id(self, value):
        if not isinstance(value, int):
            raise ValueError('Last used annotation id must be an integer.')
        if value < self.last_used_annotation_id:
            raise ValueError('Cannot decrease last used annotation id.')
        self.last_used_annotation_id_element.text = str(value)

    def assign_children(self):
        """
        Assigns children to tiers and annotations. Elements without children are marked as childless to differentiate
        them from elements that have not been assigned children for some reason.
        :return:
        """
        for tier in self.tiers.values():
            if tier.parent_ref is not None:
                tier.parent.append_child(tier)

        for tier in self.tiers.values():
            if tier.children_assigned is False:
                tier.mark_as_childless()

        for annotation in self.annotations.values():
            if annotation.annotation_type == Annotation.REF_ANNOTATION:
                annotation.parent.append_child(annotation)

        for annotation in self.annotations.values():
            if annotation.children_assigned is False:
                annotation.mark_as_childless()

    def update_cve_refs(self):
        """
        See Annotation.update_cve_ref().
        """
        for tier in self.tiers.values():
            if not tier.uses_cv:
                continue

            for annotation in tier.annotations.values():
                annotation.update_cve_ref()

    def to_eaf(self, path):
        self.to_file(path)

    def insert_after(self, inserted_element: EafElement, after_element: EafElement):
        parent_element = self.find_parent(after_element.element)
        parent_element.insert(list(parent_element).index(after_element.element) + 1, inserted_element.element)

    def _insert_element_in_order(self, eaf_element_to_insert: EafElement):
        """Helper to insert an EafElement's XML element into the root, maintaining a preferred order."""
        root = self.tree.getroot()
        insert_after_xml_element = None
        xml_element_to_insert = eaf_element_to_insert.element
        element_tag = eaf_element_to_insert.TAG

        # Determine fallback_tags_in_order dynamically
        try:
            current_element_index = self.EAF_ELEMENT_ORDER.index(element_tag)
            fallback_tags_in_order = list(self.EAF_ELEMENT_ORDER[:current_element_index])
            fallback_tags_in_order.reverse()
        except ValueError:
            # Tag not in EAF_ELEMENT_ORDER, raise an error.
            raise ValueError(
                f"Element tag '{element_tag}' is not defined in EAF_ELEMENT_ORDER. "
                f"Cannot determine insertion order. Please add it to EafTree.EAF_ELEMENT_ORDER."
            )


        # Try to insert after the last element of the same tag
        existing_elements_of_same_tag = [el for el in root if el.tag == element_tag]
        if existing_elements_of_same_tag:
            insert_after_xml_element = existing_elements_of_same_tag[-1]
        else:
            # Fallback to inserting after the last element of a preceding type
            for fallback_tag in fallback_tags_in_order:
                fallback_elements = [el for el in root if el.tag == fallback_tag]
                if fallback_elements:
                    insert_after_xml_element = fallback_elements[-1]
                    break
            else:
                # If no fallback elements found, try to insert after HEADER
                try:
                    insert_after_xml_element = self.find_single_element('HEADER')
                except ValueError:
                    pass # insert_after_xml_element remains None

        if insert_after_xml_element is not None:
            # Perform insertion directly using XML elements
            parent = self.find_parent(insert_after_xml_element)
            index = list(parent).index(insert_after_xml_element)
            parent.insert(index + 1, xml_element_to_insert)
        else:
            # Fallback: insert at the beginning of the root
            # This handles cases like an empty EAF or EAF without a HEADER
            root.insert(0, xml_element_to_insert)

    def add_external_reference(self, ext_ref_id, type_val, value_val):
        """Adds an external reference to the EAF tree."""
        if ext_ref_id in self.external_references:
            raise ValueError(f"External Reference with ID '{ext_ref_id}' already exists.")

        ext_ref_element = ExternalReference.make_xml_element(ext_ref_id, type_val, value_val)
        added_ext_ref = ExternalReference(ext_ref_element) # Assuming __init__ doesn't require eaf_tree

        self._insert_element_in_order(added_ext_ref) 
        self.external_references[added_ext_ref.id] = added_ext_ref
        return added_ext_ref

    def add_controlled_vocabulary(self, cv_id, description_text=None, ext_ref_id=None, entries=None, lang_ref="und"):
        """Adds a controlled vocabulary to the EAF tree."""
        if cv_id in self.controlled_vocabularies:
            raise ValueError(f"Controlled Vocabulary with ID '{cv_id}' already exists.")
        if ext_ref_id and ext_ref_id not in self.external_references:
            raise ValueError(f"External Reference ID '{ext_ref_id}' not found in EAF tree.")

        cv_element = ControlledVocabulary.make_xml_element(cv_id, description_text, ext_ref_id, entries, lang_ref)
        added_cv = ControlledVocabulary(cv_element, eaf_tree=self)

        self._insert_element_in_order(added_cv)
        self.controlled_vocabularies[added_cv.id] = added_cv
        return added_cv

    def add_linguistic_type(self, linguistic_type_id, time_alignable: bool, graphic_references: bool,
                            constraints_ref=None, cv_ref=None):
        """Adds a linguistic type to the EAF tree."""
        if linguistic_type_id in self.linguistic_types:
            raise ValueError(f"Linguistic Type with ID '{linguistic_type_id}' already exists.")
        if cv_ref and cv_ref not in self.controlled_vocabularies:
            # Similar to CV's EXT_REF, assume CV should exist if referenced.
            raise ValueError(f"Controlled Vocabulary ID '{cv_ref}' not found for Linguistic Type.")

        lt_element = LinguisticType.make_xml_element(linguistic_type_id, time_alignable, graphic_references,
                                                     constraints_ref, cv_ref)
        added_lt = LinguisticType(lt_element, eaf_tree=self)

        self._insert_element_in_order(added_lt)
        self.linguistic_types[added_lt.id] = added_lt
        return added_lt

    def _add_dependent_tier(self, tier_id, linguistic_type_ref, parent_tier):
        """
        Add a dependent tier to the EAF tree.

        Args:
            tier_id: The ID of the tier
            linguistic_type_ref: The linguistic type reference
            parent_tier: The parent tier

        Returns:
            The added Tier instance
        """
        # Create a new XML element and add it to the tree
        tier_element = Tier.make_xml_element(tier_id=tier_id, linguistic_type_ref=linguistic_type_ref,
                                             participant=parent_tier.participant, parent_ref=parent_tier.id)
        added_tier = Tier(tier_element, eaf_tree=self)
        self.insert_after(inserted_element=added_tier, after_element=parent_tier)

        # Add the new tier to the list of tiers and assign it as a child to the parent tier
        self.tiers[tier_id] = added_tier
        parent_tier.append_child(added_tier)

        # Copy all annotations from the parent tier to the new tier - without values
        for parent_annotation in parent_tier.annotations.values():
            added_annotation = added_tier.add_reference_annotation(parent_annotation_id=parent_annotation.id)
            parent_annotation.append_child(added_annotation)

        return added_tier

    def _add_independent_tier(self, tier_id, linguistic_type_ref, participant):

        # Create the tier element with no parent_ref
        tier_element = Tier.make_xml_element(
            tier_id=tier_id,
            linguistic_type_ref=linguistic_type_ref,
            participant=participant,
            parent_ref=None
        )
        added_tier = Tier(tier_element, eaf_tree=self)

        self._insert_element_in_order(added_tier)

        # Register the tier
        self.tiers[tier_id] = added_tier
        added_tier.mark_as_childless()

        return added_tier

    def add_tier(self, tier_id, linguistic_type, participant=None, parent_tier=None):
        """
        Add a tier to the EAF tree.
        """
        if participant is None and parent_tier is None:
            raise ValueError('Either participant or parent_tier must be provided.')
        if participant is not None and parent_tier is not None:
            raise ValueError('Only one of participant and parent_tier can be provided.')

        if tier_id in self.tiers:
            raise ValueError(f'Tier with id {tier_id} already exists.')

        if parent_tier is not None:
            basic_chi_tiers = ('vcm@CHI', 'lex@CHI', 'mwu@CHI')
            if parent_tier.participant == 'CHI' and tier_id in basic_chi_tiers:
                # The only reason this can be needed is that the wrong template was used to create the EAF file. For
                # these cases, we should add some age-based checks before adding anything.
                raise NotImplementedError('Adding CHI\'s dependent tiers is not supported.')

            if '@' not in tier_id:
                raise ValueError('Tier id must contain the participant after "@" when adding a dependent tier.')

            tier_kind, participant_from_id = tier_id.split('@')
            if participant_from_id != parent_tier.participant:
                raise ValueError('The participant in the tier id must match the participant of the parent tier.')

            if linguistic_type.lower() != tier_kind.lower():
                raise ValueError('The linguistic type in the tier id must match the linguistic type of the parent tier.')

            if linguistic_type not in self.linguistic_types:
                raise ValueError(f'The linguistic type {linguistic_type} must be defined in the EAF file.')

            return self._add_dependent_tier(tier_id, linguistic_type, parent_tier)

        # Independent tier
        if participant is not None and '@' in tier_id:
            tier_kind, participant_from_id = tier_id.split('@')
            if participant != participant_from_id:
                raise ValueError('The participant in the tier id must match the participant argument.')
            if linguistic_type.lower() != tier_kind.lower():
                raise ValueError('The linguistic type in the tier id must match the tier id prefix.')

        if linguistic_type not in self.linguistic_types:
            raise ValueError(f'The linguistic type {linguistic_type} must be defined in the EAF file.')

        return self._add_independent_tier(tier_id, linguistic_type, participant)

    def drop_tier(self, tier_id):
        if tier_id not in self.tiers:
            raise ValueError(f'Tier {tier_id} does not exist.')

        tier = self.tiers[tier_id]

        if len(tier.annotations) > 0:
            raise ValueError(f'Tier {tier_id} has annotations and cannot be dropped.')

        if len(tier.children) > 0:
            raise ValueError(f'Tier {tier_id} has child tiers and cannot be dropped.')

        if tier.parent_ref is not None:
            tier.parent.children.remove(tier)
        del self.tiers[tier_id]
        self.tree.getroot().remove(tier.element)

    def create_time_slot(self, time_value_ms):
        """
        Create a new time slot for the given time value.

        Args:
            time_value_ms: Time value in milliseconds

        Returns:
            ID of the newly created time slot
        """
        # Find or create the TIME_ORDER element
        try:
            time_order_element = self.find_single_element('TIME_ORDER')
        except ValueError:
            # TIME_ORDER element doesn't exist yet, create it after HEADER
            root = self.tree.getroot()
            header_element = self.find_single_element('HEADER')
            time_order_element = element_tree.Element('TIME_ORDER')

            # Find the index of the HEADER element among its siblings
            header_index = list(root).index(header_element)
            # Insert TIME_ORDER after HEADER
            root.insert(header_index + 1, time_order_element)

        # Generate new time slot ID
        existing_time_slots = list(self.time_slots.keys())
        if existing_time_slots:
            last_id_num = max(int(ts_id[2:]) for ts_id in existing_time_slots)
            new_id_num = last_id_num + 1
        else:
            new_id_num = 1

        time_slot_id = f'ts{new_id_num}'

        # Create the time slot element
        time_slot_element = element_tree.Element(TimeSlot.TAG,
                                                 attrib={TimeSlot.ID: time_slot_id,
                                                         TimeSlot.TIME_VALUE: str(time_value_ms)})

        # Add it to the TIME_ORDER element
        time_order_element.append(time_slot_element)

        # Create the TimeSlot object and add it to eaf_tree.time_slots
        time_slot = TimeSlot(time_slot_element, self)
        self.time_slots[time_slot_id] = time_slot

        return time_slot_id
