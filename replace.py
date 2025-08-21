import os
import argparse


def is_file_and_starts_with(filename: str, folder_path: str, prefix: str) -> bool:
    path = os.path.join(folder_path, filename)

    return os.path.isfile(path) and filename.startswith(prefix)


def build_errors_hash(errors: list) -> dict:
    errors_hash = {}
    for error in errors:
        file = error['file']
        reason = str(error['reason'])
        if reason not in errors_hash:
            errors_hash[reason] = []
        errors_hash[reason].append(file)

    return errors_hash


def build_error_msg(errors: list) -> str:
    errors_hash = build_errors_hash(errors)
    error_report = ''
    for reason, files in errors_hash.items():
        files_list = '\n\t'.join(files)
        error_report += f"{reason}:\n\t{files_list}\n"

    if error_report == '':
        return ''

    return 'В ходе выполнения возникли следующие ошибки:\n' + error_report


def build_report_msg(raw_report: dict) -> str:
    if raw_report['total'] == 0:
        return 'В папке не найдены файлы'

    if raw_report['found'] == 0:
        return f'В папке отсутствуют файлы с префиксом {raw_report["prefix"]}'

    output = f'В папке {raw_report["folder_path"]} найдено {raw_report["found"]} файлов с префиксом "{raw_report["prefix"]}", успешно переименовано {raw_report["renamed"]}.'

    if len(raw_report['errors']) != 0:
        output = f'{output}\n' + build_error_msg(raw_report['errors'])

    return output


def replace(folder_path: str, prefix: str, replacement: str) -> dict:
    total, found, renamed, errors = 0, 0, 0, []

    for filename in os.listdir(folder_path):
        total += 1
        path = os.path.join(folder_path, filename)

        if not os.path.isfile(path) or not filename.startswith(prefix):
            continue

        found += 1
        new_filename = filename.replace(prefix, replacement)
        new_path = os.path.join(folder_path, new_filename)

        try:
            os.rename(path, new_path)
            renamed += 1
        except Exception as e:
            errors.append({
                'file': filename,
                'reason': e
            })

    return {
        'folder_path': folder_path,
        'prefix': prefix,
        'total': total,
        'found': found,
        'renamed': renamed,
        'errors': errors
    }

if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Программа по массовому отрезанию префикса от файлов в каталоге')

    parser.add_argument("--in", type=str, help='Каталог в котором будет происходить переименование', required=True)
    parser.add_argument("--prefix", type=str, help='Префикс, который по которому будут отбираться файлы для переименования', required=True)
    parser.add_argument("--to", type=str, help='Строка на которую будет заменён префикс, в переименовываемом файле', default='')

    args = parser.parse_args()

    print(build_report_msg(replace(getattr(args, 'in'), args.prefix, args.to)))
