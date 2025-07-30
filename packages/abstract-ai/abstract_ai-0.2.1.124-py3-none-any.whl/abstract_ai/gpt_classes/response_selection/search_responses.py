import os,re
from abstract_utilities import *
from abstract_solcatcher_database import get_timestamp_from_data
def detect_language_from_text(text: str):
    ts_patterns = [
        r'\binterface\s+\w+\s*{', 
        r'\btype\s+\w+\s*=', 
        r'\blet\s+\w+:\s+\w+', 
        r'\bfunction\s+\w+\s*\(', 
        r'\bimport\s+.*\s+from\s+[\'"]', 
        r'\bexport\s+(default|function|const|class)'
    ]
    py_patterns = [
        r'\bdef\s+\w+\(', 
        r'\bclass\s+\w+\s*:', 
        r'\bimport\s+\w+', 
        r'\bfrom\s+\w+\s+import\s+\w+', 
        r'\bif\s+__name__\s*==\s*["\']__main__["\']', 
        r'@\w+', 
        r'\blambda\s+'
    ]
    ts_score = sum(1 for pattern in ts_patterns if re.search(pattern, text))
    py_score = sum(1 for pattern in py_patterns if re.search(pattern, text))
    if ts_score > py_score and ts_score > 0:
        return "TypeScript"
    elif py_score > ts_score and py_score > 0:
        return "Python"
    elif ts_score == py_score == 0:
        return "Neither"
    else:
        return "Uncertain"
class PathManager:
    @staticmethod
    def get_abs_path():
        return os.path.abspath(__file__)

    @staticmethod
    def get_abs_dir():
        return os.path.dirname(PathManager.get_abs_path())

    @staticmethod
    def create_abs_path(relative_path):
        return os.path.join(PathManager.get_abs_dir(), relative_path)

    @staticmethod
    def search_for_file(filename, base_dirs):
        for base in base_dirs:
            for root, _, files in os.walk(base):
                if filename in files:
                    return os.path.join(root, filename)
        return None

    @staticmethod
    def get_conversation_path():
        filename = 'conversations.json'
        # Priority: abs dir, cwd, ~/Documents
        abs_dir = PathManager.get_abs_dir()
        cwd = os.getcwd()
        docs = os.path.expanduser('~/Documents')

        # Try non-recursive checks first
        for location in [abs_dir, cwd, docs]:
            candidate = os.path.join(location, filename)
            if os.path.isfile(candidate):
                return candidate

        # Fall back to recursive search in ~/Documents
        found_path = PathManager.search_for_file(filename, [docs])
        if found_path:
            return found_path

        raise FileNotFoundError(f"'{filename}' not found in script dir, CWD, or ~/Documents.")


def get_conversation_data(file_path=None):
    file_path = get_convo_path(file_path=file_path)
    return safe_read_from_json(file_path)


def is_valid_time(comp_timestamp, timestamp=None, before=True):
    if timestamp is None:
        return True
    return (timestamp >= comp_timestamp) if before else (timestamp <= comp_timestamp)


def find_for_string(string, parts):
    return [part for part in parts if string.lower() in str(part).lower()]


def is_strings_in_string(strings, parts):
    if not strings:
        return parts
    strings = make_list(strings)
    for string in strings:
        parts = find_for_string(string, parts)
        if not parts:
            return []
    return parts


def get_parts(data):
    parts = []
    for path in find_paths_to_key(json_data=data, key_to_find="message"):
        message_value = get_value_from_path(data, path)
        for sub_path in find_paths_to_key(message_value, 'parts'):
            parts_value = get_value_from_path(message_value, sub_path)
            parts.extend([p for p in parts_value if p])
    return parts
def get_convo_path(file_path=None):
    file_path = file_path or PathManager.get_conversation_path()
    return file_path
class ConversationManager(metaclass=SingletonMeta):
    def __init__(self,file_path=None):
        
        if not hasattr(self, 'initialized') or self.initialized == False:
            self.initialized = True
            self.original_file_path = file_path
            self.convo_path = get_convo_path(file_path=file_path)
            self.conversation_data = get_conversation_data(self.convo_path)
        
def get_conversation_manager(file_path=None):
    conversation_mgr = ConversationManager(file_path=file_path)
    if conversation_mgr.original_file_path != file_path:
        conversation_mgr.initialized = False
        conversation_mgr = ConversationManager(file_path=file_path)
    return conversation_mgr

def get_convo_data(file_path=None):
    conversation_mgr = get_conversation_manager(file_path=file_path)
    return conversation_mgr.conversation_data
def search_code(code,parts):
    found_code = []
    for datas in parts:
        for data in make_list(datas):
            if detect_language_from_text(data) not in make_list(code):
                found_code.append(data)
    return found_code
def capitalize(string):
    if not string:
        return string
    string = str(string)
    if len(string)>1:
        init = string[0].upper()
        rest = string[1:].lower()
        string = f"{init}{rest}"
    else:
        string = string.upper()
    return string
def search_in_conversation(strings=None, *args, **kwargs):
    strings = make_list(strings)
    timestamp = get_timestamp_from_data(kwargs)
    before = kwargs.get('before', True)
    python = kwargs.get('python')
    typescript = kwargs.get('typescript')
    uncertain = kwargs.get('uncertain')
    neither = kwargs.get('neither')
    code = [capitalize(code) for code in [neither,uncertain,python,typescript] if code]
    file_path = kwargs.get('file_path', None)
    results = []
    for convo in get_convo_data(file_path=file_path):
        create_time = make_list(get_any_value(convo, 'create_time'))[0]
        if is_valid_time(comp_timestamp=create_time, timestamp=timestamp, before=before):
            parts = get_parts(convo)
            matched_parts = is_strings_in_string(strings, parts)
            if matched_parts:
                results.append(matched_parts)
    if code:
        search_code(code,results)
    return results
