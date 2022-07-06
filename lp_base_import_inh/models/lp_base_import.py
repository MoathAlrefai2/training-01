# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import UserError
from datetime import datetime
import tempfile
try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None
from odoo import fields, models, _
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter
import psycopg2
import logging
_logger = logging.getLogger(__name__)

class Import(models.TransientModel):

    _inherit = 'base_import.import'

    is_conv = fields.Boolean(default=False)

    def do(self, fields, columns, options, dryrun=False):
        self.ensure_one()
        self._cr.execute('SAVEPOINT import')

        try:
            data, import_fields = self._convert_import_data(fields, options)
            # Parse date and float field
            data = self._parse_import_data(data, import_fields, options)
        except ValueError as error:
            return {
                'messages': [{
                    'type': 'error',
                    'message': str(error),
                    'record': False,
                }]
            }

        _logger.info('importing %d rows...', len(data))
        name_create_enabled_fields = options.pop('name_create_enabled_fields', {})
        if options.get('c_import'):
            try:
                assert 'employee_id' in import_fields, 'Can not import without Employee field'
            except Exception as error:
                return {
                'messages': [{
                    'type': 'error',
                    'message': str(error),
                    'record': False,
                }]
            }
            name_create_enabled_fields['task_id'] = True
        import_limit = options.pop('limit', None)
        model = self.env[self.res_model].with_context(import_file=True, name_create_enabled_fields=name_create_enabled_fields, _import_limit=import_limit)
        import_result = model.load(import_fields, data)
        _logger.info('done')

        try:
            if dryrun:
                self._cr.execute('ROLLBACK TO SAVEPOINT import')
                # cancel all changes done to the registry/ormcache
                self.pool.clear_caches()
                self.pool.reset_changes()
            else:
                self._cr.execute('RELEASE SAVEPOINT import')
        except psycopg2.InternalError:
            pass

        # Insert/Update mapping columns when import complete successfully
        if import_result['ids'] and options.get('headers'):
            BaseImportMapping = self.env['base_import.mapping']
            for index, column_name in enumerate(columns):
                if column_name:
                    # Update to latest selected field
                    mapping_domain = [('res_model', '=', self.res_model), ('column_name', '=', column_name)]
                    column_mapping = BaseImportMapping.search(mapping_domain, limit=1)
                    if column_mapping:
                        if column_mapping.field_name != fields[index]:
                            column_mapping.field_name = fields[index]
                    else:
                        BaseImportMapping.create({
                            'res_model': self.res_model,
                            'column_name': column_name,
                            'field_name': fields[index]
                        })
        if 'name' in import_fields:
            index_of_name = import_fields.index('name')
            skipped = options.get('skip', 0)
            # pad front as data doesn't contain anythig for skipped lines
            r = import_result['name'] = [''] * skipped
            # only add names for the window being imported
            r.extend(x[index_of_name] for x in data[:import_limit])
            # pad back (though that's probably not useful)
            r.extend([''] * (len(data) - (import_limit or 0)))
        else:
            import_result['name'] = []

        skip = options.get('skip', 0)
        # convert load's internal nextrow to the imported file's
        if import_result['nextrow']: # don't update if nextrow = 0 (= no nextrow)
            import_result['nextrow'] += skip

        return import_result
    
    def parse_preview(self, options, count=10):
        options['name_create_enabled_fields']['task_id'] = True
        if not self.is_conv or not options.get('sheet'):
            self.is_conv = True
            template_name = options.get('c_import')
            book = xlrd.open_workbook(file_contents = self.file)
            temp_file = tempfile.NamedTemporaryFile(suffix=".xlsx")
            workbook = xlsxwriter.Workbook(temp_file.name)

            if not template_name and self.res_model == 'account.analytic.line':
                raise UserError(_("Please Select Template!"))
            # try:
            if template_name:
                res = self.get_converted_file(book, template_name, workbook, temp_file)
                if not type(res) == bytes:
                    return res
                else:
                    self.file = res
            return super(Import,self).parse_preview(options, count)
                
            # except:
            #     raise UserError(_("Please upload appropriate file!"))
        else:
            return super(Import,self).parse_preview(options, count)

    def get_converted_file(self, book, template_name, workbook, temp_file):
        if template_name == "ooredoo":
            return self.convert_ooredoo_file(book, workbook, temp_file)
        elif template_name == 'aramex':
            return self.convert_aramex_file(book, workbook, temp_file)
        elif template_name == 'virgin':
            return self.convert_virgin_file(book, workbook, temp_file)
        elif template_name == 'diwan':
            return self.convert_diwan_file(book, workbook, temp_file)
        elif template_name == 'lp-general':
            return self.convert_lp_general_file(book, workbook, temp_file)

    def convert_ooredoo_file(self, book, workbook, temp_file):
        cols_list = ['Employee', 'Date', 'Quantity', 'Project', 'Task'] 
        dataDict = self.define_dict_keys(cols_list)

        number_of_sheets = len(book.sheet_names())
        if number_of_sheets == 1:
            sheet_name = book.sheet_names()[0]
            number_of_rows = int(book.sheet_by_name(sheet_name).nrows)
            dataDict = self.read_ooredoo_file(book, number_of_rows, sheet_name, dataDict)
            if dataDict.get('error'):
                return dataDict
            workbook = self.write_single_sheet(workbook, sheet_name, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()
            return data
        else:
            workbook = self.write_empty_sheet(workbook,dataDict)
            for sheet in book.sheet_names():
                dataDict = self.clear_dict_values(dataDict)
                number_of_rows = int(book.sheet_by_name(sheet).nrows)
                dataDict = self.read_ooredoo_file(book, number_of_rows, sheet, dataDict)
                if dataDict.get('error'):
                    return dataDict
                workbook = self.write_single_sheet(workbook, sheet, dataDict)
                
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data

    def read_ooredoo_file(self, book, number_of_rows, sheet_name, dataDict):
        for row in range(1,number_of_rows):
            if self.check_last_row(book, number_of_rows, row, sheet_name):
                continue
            else:
                dataDict['Project'].append(self.extract_cell_data(book, sheet_name, row, 5))
                dataDict['Task'].append('Default Task')
                try:
                    emp = self.extract_cell_data(book, sheet_name, row, 4)
                    assert emp, "One (or more) of records doesn't has employee, Please fill it"
                    dataDict['Employee'].append(emp)
                except Exception as error:
                    return {
                    'error': str(error),
                    }
                dataDict['Quantity'].append(self.extract_cell_data(book, sheet_name, row, 2))
        # Read & Convert Date
        for row in range(1,number_of_rows):
            if self.check_last_row( book, number_of_rows, row, sheet_name):
                continue
            else:
                seconds = (int(self.extract_cell_data(book, sheet_name, row, 0)) - 25569) * 86400.0
                formatted_date=datetime.utcfromtimestamp(seconds).date()
                dataDict['Date'].append(str(formatted_date))

        return dataDict

    def check_last_row(self, book, number_of_rows ,row, sheet_name):
        return True if row == (number_of_rows - 1) and not book.sheet_by_name(sheet_name).cell(row, 5).value else False

    def convert_aramex_file(self, book, workbook, temp_file):       
        # Define dictionary to store data on it 
        cols_list = ['Employee', 'Date', 'Quantity', 'Project', 'Task', 'Description'] 
        dataDict = self.define_dict_keys(cols_list)
        
        number_of_sheets = len(book.sheet_names())
        if number_of_sheets == 1:
            sheet_name = book.sheet_names()[0]
            number_of_rows = int(book.sheet_by_name(sheet_name).nrows)
            dataDict = self.read_aramex_file(book, number_of_rows, sheet_name, dataDict)
            if dataDict.get('error'):
                return dataDict
            workbook = self.write_single_sheet(workbook, sheet_name, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data
        else:
            workbook = self.write_empty_sheet(workbook,dataDict)
            for sheet in book.sheet_names():
                dataDict = self.clear_dict_values(dataDict)
                number_of_rows = int(book.sheet_by_name(sheet).nrows)
                dataDict = self.read_aramex_file(book, number_of_rows, sheet, dataDict)
                if dataDict.get('error'):
                    return dataDict
                workbook = self.write_single_sheet(workbook, sheet, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data

    def read_aramex_file(self, book, number_of_rows, sheet_name, dataDict):
        for row in range(1,number_of_rows):
            dataDict['Project'].append(self.extract_cell_data(book, sheet_name, row, 2))
            dataDict['Task'].append('Default Task')
            try:
                emp = self.extract_cell_data(book, sheet_name, row, 1)
                assert emp, "One (or more) of records doesn't has employee, Please fill it"
                dataDict['Employee'].append(emp)
            except Exception as error:
                return {
                    'error': str(error),
                    }
            dataDict['Quantity'].append(self.extract_cell_data(book, sheet_name, row, 6))
            dataDict['Description'].append(self.extract_cell_data(book, sheet_name, row, 7))

        # Read & Convert Date
        for row in range(1,number_of_rows):
            seconds = (self.extract_cell_data(book, sheet_name, row, 3) - 25569) * 86400.0
            formatted_date=datetime.utcfromtimestamp(seconds).date()
            dataDict['Date'].append(str(formatted_date))
        
        return dataDict

    def convert_virgin_file(self, book, workbook, temp_file):
        # Define dictionary to store data on it
        cols_list = ['Employee', 'Project', 'Date', 'Quantity', 'Task'] 
        dataDict = self.define_dict_keys(cols_list)

        number_of_sheets = len(book.sheet_names())
        if number_of_sheets == 1:
            sheet_name = book.sheet_names()[0]
            number_of_cols = int(book.sheet_by_name(sheet_name).ncols)
            number_of_rows = book.sheet_by_name(sheet_name).nrows - 1
            dataDict = self.read_virgin_file(book, number_of_cols, number_of_rows, sheet_name, dataDict)
            if dataDict.get('error'):
                return dataDict
            workbook = self.write_single_sheet(workbook, sheet_name, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data
        else:
            workbook = self.write_empty_sheet(workbook,dataDict)
            for sheet in book.sheet_names():
                dataDict = self.clear_dict_values(dataDict)
                number_of_cols = int(book.sheet_by_name(sheet).ncols)
                number_of_rows = book.sheet_by_name(sheet).nrows - 1
                dataDict = self.read_virgin_file(book, number_of_cols, number_of_rows, sheet, dataDict)
                if dataDict.get('error'):
                    return dataDict
                workbook = self.write_single_sheet(workbook, sheet, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data
    
    def read_virgin_file(self, book, number_of_cols, number_of_rows, sheet_name, dataDict):
        for col in range(6, number_of_cols):
            for row in range(1, number_of_rows):
                dataDict['Project'].append(self.extract_cell_data(book, sheet_name, row, 3))
                try:
                    emp = self.extract_cell_data(book, sheet_name, row, 2)
                    assert emp, "One (or more) of records doesn't has employee, Please fill it"
                    dataDict['Employee'].append(emp)
                except Exception as error:
                    return {
                        'error': str(error),
                    }
                dataDict['Quantity'].append(self.extract_cell_data(book, sheet_name, row, col))
                dataDict['Task'].append('Default Task')

        # Read & Convert Date
        for col in range(6,number_of_cols):
            for row in range(1, number_of_rows):
                date_obj = datetime.strptime(self.extract_cell_data(book, sheet_name, 0, col),'%d/%b/%y')
                date_obj = date_obj.strftime('%Y-%m-%d')
                dataDict['Date'].append(date_obj)

        return dataDict

    def convert_diwan_file(self, book, workbook, temp_file):
        # Define dictionary to store data on it
        cols_list = ['Employee', 'Project', 'Date', 'Quantity','Task'] 
        dataDict = self.define_dict_keys(cols_list)

        number_of_sheets = len(book.sheet_names())
        if number_of_sheets == 1:
            sheet_name = book.sheet_names()[0]
            number_of_rows = int(book.sheet_by_name(sheet_name).nrows)
            number_of_cols = int(book.sheet_by_name(sheet_name).ncols)
            dataDict = self.read_diwan_file(book, number_of_rows, number_of_cols, sheet_name, dataDict)
            if dataDict.get('error'):
                return dataDict
            workbook = self.write_single_sheet(workbook, sheet_name, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data
        else:
            workbook = self.write_empty_sheet(workbook,dataDict)
            for sheet in book.sheet_names():
                dataDict = self.clear_dict_values(dataDict)
                number_of_rows = int(book.sheet_by_name(sheet).nrows)
                number_of_cols = int(book.sheet_by_name(sheet).ncols)
                dataDict = self.read_diwan_file(book, number_of_rows, number_of_cols, sheet, dataDict)
                if dataDict.get('error'):
                    return dataDict
                workbook = self.write_single_sheet(workbook, sheet, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data

    def read_diwan_file(self, book, number_of_rows, number_of_cols, sheet_name, dataDict):
        for row in range(4,number_of_rows):
            for col in range(1, number_of_cols):
                try:
                    emp = self.extract_cell_data(book, sheet_name, 3, col)
                    assert emp, "One (or more) of records doesn't has employee, Please fill it"
                    dataDict['Employee'].append(emp)
                except Exception as error:
                    return {
                        'error': str(error),
                    }   
                dataDict['Quantity'].append(self.extract_cell_data(book, sheet_name, row, col))
                dataDict['Project'].append(self.extract_cell_data(book, sheet_name, 1, 1))
                dataDict['Task'].append('Default Task')

        # Read & Convert Date
        for row in range(4,number_of_rows):
            for col in range(1, number_of_cols):
                seconds = (self.extract_cell_data(book, sheet_name, row, 0) - 25569) * 86400.0
                formatted_date=datetime.utcfromtimestamp(seconds).date()
                dataDict['Date'].append(str(formatted_date))

        return dataDict
        
    def convert_lp_general_file(self, book, workbook, temp_file):       
        # Define dictionary to store data on it
        cols_list = ['Employee', 'Date', 'Quantity', 'Project', 'Task'] 
        dataDict = self.define_dict_keys(cols_list)
        
        number_of_sheets = len(book.sheet_names())
        if number_of_sheets == 1:
            sheet_name = book.sheet_names()[0]
            number_of_rows = int(book.sheet_by_name(sheet_name).nrows)
            dataDict = self.read_lp_general_file(book, number_of_rows, sheet_name, dataDict)
            if dataDict.get('error'):
                return dataDict
            workbook = self.write_single_sheet(workbook, sheet_name, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data
        else:
            workbook = self.write_empty_sheet(workbook,dataDict)
            for sheet in book.sheet_names():
                dataDict = self.clear_dict_values(dataDict)
                number_of_rows = int(book.sheet_by_name(sheet).nrows)
                dataDict = self.read_lp_general_file(book, number_of_rows, sheet, dataDict)
                if dataDict.get('error'):
                    return dataDict
                workbook = self.write_single_sheet(workbook, sheet, dataDict)
            workbook.close()
            data = open(temp_file.name, 'rb').read()
            temp_file.close()

            return data

    def read_lp_general_file(self, book, number_of_rows, sheet_name, dataDict):
        for row in range(1,number_of_rows):
            dataDict['Project'].append(self.extract_cell_data(book, sheet_name, row, 1))
            dataDict['Task'].append('Default Task')
            try:
                emp = self.extract_cell_data(book, sheet_name, row, 0)
                assert emp, "One (or more) of records doesn't has employee, Please fill it"
                dataDict['Employee'].append(emp)
            except Exception as error:
                return {
                    'error': str(error),
                    }
            dataDict['Quantity'].append(self.extract_cell_data(book, sheet_name, row, 4))

        # Read & Convert Date
        for row in range(1,number_of_rows):
            seconds = (self.extract_cell_data(book, sheet_name, row, 2) - 25569) * 86400.0
            formatted_date=datetime.utcfromtimestamp(seconds).date()
            dataDict['Date'].append(str(formatted_date))
        
        return dataDict

    def extract_cell_data(self, book, sheet_name, row_num, col_num):
        val = book.sheet_by_name(sheet_name).cell(row_num, col_num).value
        if type(val) == str:
            return val.strip()        
        else:
            return val
    
    def define_dict_keys(self, keys_list):
        dataDict = {}
        for key in keys_list:
            dataDict[key] = []
        return dataDict

    def write_single_sheet(self, workbook, sheet_name, dataDict):
        sheet = workbook.add_worksheet('TimeSheet ' + sheet_name)
        bold_line = workbook.add_format({'align': 'left','font_size': 10, 'bold': 1, })
        excel_col = ord('A')
        for key in dataDict.keys():
            sheet.write(chr(excel_col) + str(1), key, bold_line)
            excel_col += 1
        excel_row = 2
        excel_col = ord('A')

        for key, list in dataDict.items():
            for rec in list:
                sheet.write(chr(excel_col) + str(excel_row), rec)
                excel_row +=1 
            excel_row = 2
            excel_col+=1
            
        return workbook

    def write_empty_sheet(self, workbook, dataDict):
        empty_sheet = workbook.add_worksheet('Please Select Sheet')
        bold_line = workbook.add_format({'align': 'left','font_size': 10, 'bold': 1, })
        excel_col = ord('A')
        for key in dataDict.keys():
            empty_sheet.write(chr(excel_col) + str(1), key, bold_line)
            excel_col += 1
        empty_sheet.write(chr(ord('A')) + str(2), 'This is empty sheet')

        return workbook

    def clear_dict_values(self, dataDict):
        newDataDict = {}
        for key in dataDict.keys():
            newDataDict[key] = []

        return newDataDict