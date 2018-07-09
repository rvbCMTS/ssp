import os


def import_personnel_dosimetry_report(vendor: str, input_file_directory: str, output_file_directory: str):
    if not os.path.exists(input_file_directory):
        raise ValueError('The input file directory does not exist')
    if vendor.lower() == 'landauer':
        from .tools.read_landauer_reports import parse_reports
        parse_reports(input_file_directory, output_file_directory)
    else:
        raise NotImplementedError(f'Import of personnel dosimetry reports not implemeted for {vendor}')

    return True
