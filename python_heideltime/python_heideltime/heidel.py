from python_heideltime import Heideltime

heideltime_parser = Heideltime()
heideltime_parser.set_language('SPANISH')
heideltime_parser.set_document_type('NEWS')
print(heideltime_parser.parse('Ayer comí macarrones'))