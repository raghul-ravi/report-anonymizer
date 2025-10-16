"""
MISMO XML Anonymizer
Anonymizes personally identifiable information (PII) in MISMO XML documents
"""

from lxml import etree
import random
from datetime import datetime, timedelta


class MISMOAnonymizer:
    """Anonymizes MISMO XML documents by replacing PII with fake data"""

    def __init__(self):
        self.name_counter = 0
        self.address_counter = 0
        self.email_counter = 0
        self.phone_counter = 0
        self.creditor_counter = 0

        # Fake names pool
        self.first_names = ["John", "Jane", "Michael", "Sarah", "Robert", "Emily", "David", "Lisa"]
        self.last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]

        # Common MISMO attribute and element patterns
        self.name_attributes = ['_FirstName', '_MiddleName', '_LastName', '_UnparsedName']
        self.ssn_attributes = ['_SSN']
        self.dob_attributes = ['_BirthDate']
        self.age_attributes = ['_AgeYears']

        # Address attributes
        self.address_attributes = {
            '_StreetAddress': lambda: f"{random.randint(100, 9999)} Main Street",
            '_City': lambda: "Anytown",
            '_State': lambda: "CA",
            '_PostalCode': lambda: "90001"
        }

    def anonymize_xml(self, xml_content: str) -> str:
        """
        Anonymize MISMO XML content

        Args:
            xml_content: XML string to anonymize

        Returns:
            Anonymized XML string
        """
        try:
            # Parse XML with recovery mode for malformed XML
            parser = etree.XMLParser(remove_blank_text=False, recover=True, huge_tree=True)
            root = etree.fromstring(xml_content.encode('utf-8'), parser)

            # Anonymize different types of PII
            self._anonymize_names(root)
            self._anonymize_ssn(root)
            self._anonymize_dob(root)
            self._anonymize_addresses(root)
            self._anonymize_creditors(root)
            self._anonymize_contact_info(root)
            self._anonymize_account_identifiers(root)

            # Convert back to string
            anonymized_xml = etree.tostring(
                root,
                pretty_print=True,
                xml_declaration=True,
                encoding='UTF-8'
            ).decode('utf-8')

            return anonymized_xml

        except Exception as e:
            raise ValueError(f"Error parsing or anonymizing XML: {str(e)}")

    def _anonymize_names(self, root):
        """Anonymize name attributes"""
        for elem in root.iter():
            # Generate a consistent fake name for this person
            if '_FirstName' in elem.attrib or '_LastName' in elem.attrib:
                fake_first = random.choice(self.first_names)
                fake_last = random.choice(self.last_names)
                fake_middle = random.choice(["A", "B", "C", "D", "E"])

                if '_FirstName' in elem.attrib:
                    elem.attrib['_FirstName'] = fake_first
                if '_MiddleName' in elem.attrib:
                    elem.attrib['_MiddleName'] = fake_middle
                if '_LastName' in elem.attrib:
                    elem.attrib['_LastName'] = fake_last
                if '_UnparsedName' in elem.attrib:
                    elem.attrib['_UnparsedName'] = f"{fake_first} {fake_middle} {fake_last}"

    def _anonymize_ssn(self, root):
        """Anonymize SSN attributes"""
        for elem in root.iter():
            if '_SSN' in elem.attrib:
                # Generate a fake SSN (9 digits without dashes for this format)
                fake_ssn = f"{random.randint(100, 999)}{random.randint(10, 99)}{random.randint(1000, 9999)}"
                elem.attrib['_SSN'] = fake_ssn

    def _anonymize_dob(self, root):
        """Anonymize date of birth and age"""
        for elem in root.iter():
            if '_BirthDate' in elem.attrib:
                # Generate a random DOB (30-50 years ago)
                years_ago = random.randint(30, 50)
                fake_date = datetime.now() - timedelta(days=years_ago * 365 + random.randint(0, 365))
                elem.attrib['_BirthDate'] = fake_date.strftime('%Y-%m-%d')

            if '_AgeYears' in elem.attrib:
                # Set age to match common age range
                elem.attrib['_AgeYears'] = str(random.randint(30, 50))

    def _anonymize_addresses(self, root):
        """Anonymize address attributes"""
        for elem in root.iter():
            for attr, generator in self.address_attributes.items():
                if attr in elem.attrib:
                    elem.attrib[attr] = generator()

    def _anonymize_creditors(self, root):
        """Anonymize creditor and mortgage company names"""
        creditor_names = [
            "ABC BANK", "XYZ CREDIT UNION", "GENERIC MORTGAGE CO",
            "SAMPLE FINANCIAL", "ANONYMOUS LENDER", "TEST BANK",
            "DEMO CREDIT CORP", "PLACEHOLDER FINANCE"
        ]

        for elem in root.iter():
            # Anonymize creditor names in _CREDITOR elements
            if elem.tag == '_CREDITOR' and '_Name' in elem.attrib:
                elem.attrib['_Name'] = random.choice(creditor_names)

            # Also anonymize requesting party names
            if elem.tag == 'REQUESTING_PARTY' and '_Name' in elem.attrib:
                elem.attrib['_Name'] = random.choice(creditor_names)

    def _anonymize_contact_info(self, root):
        """Anonymize phone numbers and emails in attributes"""
        for elem in root.iter():
            if '_Value' in elem.attrib and '_Type' in elem.attrib:
                if elem.attrib['_Type'] == 'Phone':
                    # Generate fake phone number
                    elem.attrib['_Value'] = f"555{random.randint(1000000, 9999999)}"
                elif elem.attrib['_Type'] in ['Email', 'Fax']:
                    # Generate fake fax number
                    elem.attrib['_Value'] = f"555{random.randint(1000000, 9999999)}"

    def _anonymize_account_identifiers(self, root):
        """Anonymize account identifiers and loan numbers"""
        for elem in root.iter():
            if '_AccountIdentifier' in elem.attrib:
                # Generate random account number
                elem.attrib['_AccountIdentifier'] = f"ACC{random.randint(100000000, 999999999)}"

            # Anonymize requesting party fields
            if 'InternalAccountIdentifier' in elem.attrib:
                elem.attrib['InternalAccountIdentifier'] = f"INT{random.randint(1000, 9999)}"
            if 'LenderCaseIdentifier' in elem.attrib:
                elem.attrib['LenderCaseIdentifier'] = f"{random.randint(1000000, 9999999)}"
            if '_RequestedByName' in elem.attrib:
                elem.attrib['_RequestedByName'] = f"user{random.randint(1, 999)}"
