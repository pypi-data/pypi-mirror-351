import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
# Sửa thành:
from parser_notam_package.ICAO_dict.ICAO_abbr import abbr
from parser_notam_package.ICAO_dict.ICAO_location import location_code_prefix
from parser_notam_package.ICAO_dict.ICAO_entity import entity
from parser_notam_package.ICAO_dict.ICAO_status import status
class NOTAMParser:
    def __init__(self):
        self.abbreviations = abbr

        self.notam_types = {
            "NOTAMN": "NEW",
            "NOTAMC": "CANCEL",
            "NOTAMR": "REPLACE"
        }

    def parse_notam_id(self, notam_text: str) -> str:
        """Parse NOTAM ID from line 1"""
        match = re.search(r'([A-Z]\d{4}/\d{2})', notam_text)
        return match.group(1) if match else "None"

    def parse_notam_type(self, notam_text: str) -> str:
        """Parse NOTAM type from line 1"""
        for code, type_name in self.notam_types.items():
            if code in notam_text:
                return type_name
        return "None"

    def parse_q_line(self, notam_text: str) -> Dict:
        """Parse Q line to get FIR, area, notam code"""
        q_match = re.search(r'Q\)\s*([^/]+)/([^/]+)/[^/]+/[^/]+/[^/]+/(\d{3})/(\d{3})/(\d{4}[NS]\d{5}[EW])(\d{3})',
                            notam_text)

        if not q_match:
            return {}

        fir = q_match.group(1)
        notam_code = q_match.group(2)
        coord_str = q_match.group(5)
        radius = int(q_match.group(6))

        # Parse coordinates
        lat_match = re.search(r'(\d{4})([NS])', coord_str)
        lon_match = re.search(r'(\d{5})([EW])', coord_str)

        area = {}
        if lat_match and lon_match:
            area = {
                'lat': lat_match.group(1) + lat_match.group(2),
                'long': lon_match.group(1) + lon_match.group(2),
                'radius': radius
            }

        return {
            'fir': fir,
            'notam_code': notam_code,
            'area': area
        }
    def parse_q_code (self,qcode:str):
        entity_code = qcode[1:3]
        status_code = qcode[3:5]

        entity_info = entity.get(entity_code, {})
        area = entity_info.get('area','')
        sub_area = entity_info.get('sub_area','')
        subject = entity_info.get('subject','')

        status_info = status.get(status_code,{})
        condition= status_info.get('condition','')
        modifier = status_info.get('modifier','')

        return  {
            'entity': entity_code,
            'area' : area,
            'sub_area': sub_area,
            'subject': subject,
            'status': status_code,
            'condition': condition,
            'modifier': modifier,
        }

    def parse_location(self, notam_text: str) -> str:
        """Parse location from field A"""
        a_match = re.search(r'A\)\s*([A-Z]{4})', notam_text)
        return a_match.group(1) if a_match else ''
    def state (self,location: str,ICAO_location:Dict) -> str:
        state = location[0:2]
        return ICAO_location.get(state)

    def parse_datetime(self, datetime_str: str) -> Optional[datetime]:
        """Parse datetime from format YYMMDDHHmm"""
        try:
            if len(datetime_str) == 10:
                year = 2000 + int(datetime_str[:2])
                month = int(datetime_str[2:4])
                day = int(datetime_str[4:6])
                hour = int(datetime_str[6:8])
                minute = int(datetime_str[8:10])
                return datetime(year, month, day, hour, minute, tzinfo=timezone.utc)
        except:
            pass
        return None

    def parse_dates(self, notam_text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        b_match = re.search(r'B\)\s*(\d{10})', notam_text)
        c_match = re.search(r'C\)\s*(\d{10})', notam_text)

        valid_from = self.parse_datetime(b_match.group(1)) if b_match else None
        valid_till = self.parse_datetime(c_match.group(1)) if c_match else None

        return valid_from, valid_till

    def parse_schedule(self, notam_text: str) -> str:
        """Parse D line to get Schedule"""
        d_match = re.search(r'D\)\s*(.*?)\s*E\)', notam_text, re.DOTALL)
        return d_match.group(1).strip() if d_match else "None"

    def parse_body(self, notam_text: str) -> str:
        """Parse E line to get body content"""
        e_match = re.search(r'E\)\s*(.*?)(?=\n[F-G]\)|$)', notam_text, re.DOTALL)
        if e_match:
            body = e_match.group(1).strip()
            body = re.sub(r'\s+', ' ', body)
            return body
        return ""

    def parse_limits(self, notam_text: str) -> Tuple[str, str]:
        f_match = re.search(r'F\)\s*([^\n\r]*)', notam_text)
        g_match = re.search(r'G\)\s*([^\n\r]*)', notam_text)

        lower_limit = f_match.group(1) if f_match else "None"
        upper_limit = g_match.group(1) if g_match else "None"

        return lower_limit, upper_limit

    def expand_abbreviations(self, text: str) -> str:
        """Expand abbreviations trong text"""
        expanded_text = text
        sorted_abbrs = sorted(self.abbreviations.items(), key=lambda x: len(x[0]), reverse=True)

        for abbr, full_form in sorted_abbrs:
            pattern = r'\b' + re.escape(abbr) + r'\b'
            expanded_text = re.sub(pattern, full_form, expanded_text, flags=re.IGNORECASE)

        return expanded_text

    def parse_notam(self, notam_text: str) -> Dict:
        """Parse complete NOTAM và trả về format mong muốn"""
        notam_id = self.parse_notam_id(notam_text)
        notam_type = self.parse_notam_type(notam_text)
        q_info = self.parse_q_line(notam_text)
        location = self.parse_location(notam_text)
        state_name = self.state(location=location,ICAO_location=location_code_prefix)
        q_code_info = self.parse_q_code(q_info.get('notam_code', ''))
        valid_from, valid_till = self.parse_dates(notam_text)
        schedule = self.parse_schedule(notam_text)
        body = self.parse_body(notam_text)
        lower_limit, upper_limit = self.parse_limits(notam_text)
        expanded_body = self.expand_abbreviations(body)
        result = {
            'extracted_fields': {
                'state': state_name,
                'id': notam_id,
                'notam_type': notam_type,
                'fir': q_info.get('fir', ''),
                'entity': q_code_info.get('entity',''),
                'status': q_code_info.get('status',''),
                'area': q_code_info.get('area',''),
                'sub_area': q_code_info.get('sub_area',''),
                'subject': q_code_info.get('subject',''),
                'condition': q_code_info.get('condition',''),
                'modifier': q_code_info.get('modifier',''),
                'airport': q_info.get('area', {}),
                'location': location,
                'notam_code': q_info.get('notam_code', ''),
                'valid_from': valid_from,
                'valid_till': valid_till,
                'schedule': schedule,
                'body': expanded_body,
                'lower_limit': lower_limit,
                'upper_limit': upper_limit
            }
        }

        return result

    def decode_notam(self, notam_text: str) -> Dict:
        expanded_text = self.expand_abbreviations(notam_text)
        decode = {
            'decode': expanded_text
        }
        return decode

    def format_output(self, parsed_result: Dict) -> str:
        """Format output"""
        fields = parsed_result['extracted_fields']

        output = f"""
Extracted Fields:
Id: {fields['id']}
Notam type: {fields['notam_type']}
FIR: {fields['fir']}
Area: {fields['area']}
Location: {fields['location']}
Notam code: {fields['notam_code']}
Valid from: {fields['valid_from']}
Valid till: {fields['valid_till']}"""

        if fields['schedule']:
            output += f"\nSchedule: {fields['schedule']}"

        output += f"""
Body: {fields['body']}
Lower limit: {fields['lower_limit']}
Upper limit: {fields['upper_limit']}"""

        return output

    def add_abbreviation(self, abbr: str, full_form: str):
        """Thêm abbreviation mới"""
        self.abbreviations[abbr.upper()] = full_form
