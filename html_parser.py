from bs4 import BeautifulSoup, NavigableString, Tag
import re
import json
import logging

class HTMLTableParser:
    def __init__(self, html_content,logger=None):
        self.soup = BeautifulSoup(self.preprocess_html(html_content), 'html.parser')
        self.logger = logger if logger else logging.getLogger(__name__)

    @staticmethod
    def preprocess_html(content):
        return re.sub(r'<\\/', '</', content)

    def extract_detailed_contents(self, td):
        def get_text_recursive(element):
            if isinstance(element, NavigableString):
                return element.strip()
            elif isinstance(element, Tag):
                return ' '.join(get_text_recursive(child) for child in element if get_text_recursive(child))
            return ''

        return get_text_recursive(td).split()

    def parse_recruiting_company_info(self, td):
        self.logger.warning("Parsing '採用企業情報'")
        company_info = {}

        ul = td.find('ul')
        if ul:
            for li in ul.find_all('li', recursive=False):
                class_name = ' '.join(li.get('class', []))
                if 'pg-job-detail-jobcassette-name' in class_name:
                    company_info['company_name'] = li.get_text(strip=True)
                    self.logger.warning(f"Company Name: {company_info['company_name']}")
                elif 'pg-job-detail-company-capital' in class_name:
                    capital_info = self.parse_capital_info(li)
                    company_info.update(capital_info)
                    self.logger.warning(f"Capital Info: {capital_info}")
                elif 'breath' in class_name:
                    company_details = self.parse_company_details(li)
                    company_info.update(company_details)
                    self.logger.warning(f"Company Details: {company_details}")

        return company_info

    def parse_capital_info(self, li):
        self.logger.warning("Parsing Capital Info")
        capital_info = {}
        for item in li.find_all('li'):
            spans = item.find_all('span')
            if len(spans) == 2:
                key = spans[0].get_text(strip=True)
                value = spans[1].get_text(strip=True)
                capital_info[key] = value
                self.logger.warning(f"Capital Info - {key}: {value}")
        return capital_info

    def parse_company_details(self, li):
        self.logger.warning("Parsing Company Details")
        details = {}
        p_text = li.find('p').get_text(separator='|', strip=True)
        for part in p_text.split('|'):
            if '】' in part:
                key, value = part.split('】', 1)
                key = key.replace('【', '').strip()
                details[key] = value.strip()
                self.logger.warning(f"Company Detail - {key}: {value}")
        return details


    def parse_qualifications(self, td):
        qualifications = {}
        raw_qualifications_text = td.get_text(separator='|', strip=True)  # Get raw text
        qualifications['raw'] = raw_qualifications_text

        current_qualification = None
        qualification_text = []

        def add_qualification():
            if current_qualification and qualification_text:
                qualifications[current_qualification] = ' '.join(qualification_text).split('・')[1:]

        for element in td.children:
            if isinstance(element, NavigableString):
                content = element.strip()
                if '】' in content:
                    add_qualification()
                    qualification_text = []
                    current_qualification = re.search(r'【.*?】', content)
                    current_qualification = current_qualification.group(0) if current_qualification else None
                elif content:
                    qualification_text.append(content)
            elif element.name == 'br':
                continue  # Skip <br> tags
            else:
                text = element.get_text(strip=True)
                if '】' in text:
                    add_qualification()
                    qualification_text = []
                    current_qualification = re.search(r'【.*?】', text).group(0)
                else:
                    qualification_text.append(text)

        add_qualification()  # Add the last set of qualifications
        return qualifications


    def parse_salary(self, td):
        salary_text = td.get_text(strip=True)
        match = re.match(r'(\d+)万～(\d+)万', salary_text)
        if match:
            lower = int(match.group(1)) * 10000  # Convert to integer
            upper = int(match.group(2)) * 10000  # Convert to integer
            return {
                'salary_text': salary_text,
                'salary_lower': lower,
                'salary_upper': upper
            }
        return salary_text  # Return original text if pattern does not match


    def conditional_parse(self, key, td):
        self.logger.warning(f"Key: {key}")
        if key == "年収":
            return self.parse_salary(td)
        if key == "採用企業情報":
            return self.parse_recruiting_company_info(td)
        if key == "応募資格":
            return self.parse_qualifications(td)
        if key in ["職種", "勤務地"]:
            return self.parse_basic_info(td)
        elif key in ["仕事内容", "労働条件"]:
            return self.parse_detailed_info(td)
        elif key in ["掲載日", "求人番号", "部署・役職名", "業種"]:
            return self.parse_general_info(td)
        else:
            return self.default_parse(td)

    def parse_basic_info(self, td):
        self.logger.warning(f"Parsing basic info")
        # Custom parsing logic for basic info
        return self.extract_detailed_contents(td)

    def parse_detailed_info(self, td):
        self.logger.warning(f"Parsing detailed info")
        # Custom parsing logic for detailed info
        return self.extract_detailed_contents(td)

    def parse_general_info(self, td):
        self.logger.warning(f"Parsing general info")
        # Custom parsing logic for general info
        return self.extract_detailed_contents(td)

    def default_parse(self, td):
        return self.extract_detailed_contents(td)

    def extract_table_data(self, table):
        data = {}
        for tr in table.find_all('tr'):
            th = tr.find('th')
            td = tr.find('td')
            if th and td:
                key = th.get_text(strip=True)
                value = self.conditional_parse(key, td)
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                data[key] = value
        return data

    def parse_tables(self, classes):
        extracted_data = {}
        for cls in classes:
            table = self.soup.find('table', class_=cls)
            if table:
                extracted_data[cls] = self.extract_table_data(table)
        return extracted_data

# Function to load HTML from a file
def load_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    html_content = load_html("your_html_file.html")
    parser = HTMLTableParser(html_content)
    parsed_data = parser.parse_tables(["pg-message-job-detail-table", "another-table-class"])
    print(json.dumps(parsed_data, indent=4, ensure_ascii=False))

