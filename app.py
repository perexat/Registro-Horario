from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime, timedelta
from odf.opendocument import OpenDocumentText
from odf.text import P, H
from odf.table import Table, TableRow, TableCell, TableColumn
from odf.style import Style, TextProperties, TableCellProperties
import re
import webbrowser
import json
import random
import os
import tempfile


app = Flask(__name__)

CLEANR = re.compile('<.*?>')


def cleanhtml(raw_html):
    cleantext = re.sub(CLEANR, '', raw_html)
    return cleantext


def is_date_in_range(date_str, date_range):
    # Convertir la fecha y el rango de fechas de strings a objetos datetime
    start_date = datetime.strptime(date_range[0], '%d/%m/%Y')
    if date_range[1] is not None:
        end_date = datetime.strptime(date_range[1], '%d/%m/%Y')
    else:
        end_date = start_date

    # Verificar si la fecha está en el rango
    return start_date <= date_str <= end_date


@app.route('/registro_horario_subir_datos', methods=['POST'])
def subir_datos():
    # Obtener el contenido del archivo enviado desde el frontend
    contenido = request.data.decode('utf-8')
    return contenido


@app.route('/registro_horario_descargar_formulario', methods=['POST'])
def descargar_datos_formulario():
    data = request.get_json()
    temp_dir = tempfile.gettempdir()
    folder = temp_dir + "/registro-horario/"

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = "datos_formulario.txt"
    random_number = str(random.randint(11111, 99999))
    random_filename = random_number + '_' + filename
    random_file_path = folder + random_filename

    # Guardar los datos JSON en un archivo de texto
    with open(random_file_path, "w") as file:
        json.dump(data, file)

    # Crear la respuesta y borrar el fichero de texto
    response = send_file(
        random_file_path,
        as_attachment=True,
        download_name=filename)
    os.remove(random_file_path)

    # Enviar el archivo de texto como respuesta para descargar
    return response


@app.route('/registro_horario_descargar_tabla_odt', methods=['POST'])
def descargar_tabla_odt():

    data = request.get_json()
    table_html = data.get('tableHtml', '')
    name = data.get('name', '')
    empresa = data.get('empresa', '')
    horascontrato = data.get('horascontrato', '')
    date_range = str(data.get('daterange', ''))
    total_hours = str(data.get('totalhours', ''))

    # Guardamos un pequeño registro de uso del programa
    logs_folder = './logs/'

    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    log_file = open(logs_folder + 'log.txt', 'a')
    formated_date = datetime.strftime(datetime.now(), "%d/%m/%y %H:%M")
    log_file.write(formated_date + ' - ' + empresa + '\n')
    log_file.close()

    # Crear un archivo ODT con la tabla de tres columnas
    odt_file = OpenDocumentText()

    # Crear un estilo de texto con color azul
    style1 = Style(name="style1", family="paragraph")
    style1_props = TextProperties(
        fontweight="bold",
        fontsize="18pt",
        color="#FFFFFF",
        backgroundcolor="#3465A4")
    style1.addElement(style1_props)

    # Crear un estilo de texto con color azul
    style2 = Style(name="style2", family="paragraph")
    style2_props = TextProperties(
        fontweight="bold",
        fontsize="12pt",
        color="#3465A4")
    style2.addElement(style2_props)

    # Agregar el estilo al documento
    odt_file.automaticstyles.addElement(style2)
    odt_file.automaticstyles.addElement(style1)

    # Crear un estilo para la cabecera de la tabla
    header_style = Style(name="HeaderStyle", family="table-cell")
    header_cell_props = TableCellProperties(
        backgroundcolor="#b4c7dc",
        border="0.5pt solid #000000")
    header_style.addElement(header_cell_props)

    # Agregar el estilo al documento
    odt_file.automaticstyles.addElement(header_style)

    # Crear un estilo para el cuerpo de la tabla
    body_style = Style(name="BodyStyle", family="table-cell")
    body_cell_props = TableCellProperties(
        backgroundcolor="#FFFFFF",
        borderleft="0.1pt solid #000000",
        borderright="0.1pt solid #000000",
        borderbottom="0.1pt solid #000000")
    body_style.addElement(body_cell_props)

    # Agregar el estilo al documento
    odt_file.automaticstyles.addElement(header_style)
    odt_file.automaticstyles.addElement(body_style)

    odt_file.text.addElement(H(
        outlinelevel=4,
        stylename=style1,
        text="Nombre: " + name))
    odt_file.text.addElement(H(
        outlinelevel=4,
        stylename=style2,
        text="Empresa: " + empresa))
    odt_file.text.addElement(H(
        outlinelevel=4,
        stylename=style2,
        text="Horas según contrato: " + horascontrato))
    odt_file.text.addElement(H(
        outlinelevel=4,
        stylename=style2,
        text="Rango de fechas: " + date_range))
    odt_file.text.addElement(H(
        outlinelevel=4,
        stylename=style2,
        text="Horas trabajadas: " + str(total_hours)))

    table = Table()

    odt_file.text.addElement(table)

    for i in range(3):
        table_column = TableColumn()
        table.addElement(table_column)

    # Parsear el contenido HTML de la tabla
    # y agregarlo a la tabla en el documento ODT
    thead = table_html.split('</thead>')[0]
    tbody = table_html.split('</thead>')[1]

    for table_section in [thead, tbody]:
        rows = table_section.split('</tr>')
        for row in rows:
            if '<tr>' in row:
                table_row = TableRow()
                table.addElement(table_row)
                if table_section == thead:
                    cells = row.split('</th>')
                else:
                    cells = row.split('</td>')
                for cell in cells:
                    if '<td>' in cell or '<th>' in cell:
                        cell = cell.replace("<br>", "--")
                        cell_content = cleanhtml(cell)

                        if cell_content[-2:] == "--":
                            # Eliminar los dos últimos caracteres si son --
                            cell_content = cell_content[:-2]

                        if table_section == thead:
                            table_cell = TableCell(stylename=header_style)
                        else:
                            table_cell = TableCell(stylename=body_style)
                        for line in cell_content.split('--'):
                            paragraph = P(text=line)
                            table_cell.addElement(paragraph)
                        table_row.addElement(table_cell)

    # Añadir celdas vacías si es necesario
    # para completar las tres columnas en cada fila
    for row in table.getElementsByType(TableRow):
        while len(row.getElementsByType(TableCell)) < 3:
            table_cell = TableCell()
            table_cell.addElement(P(text=''))
            row.addElement(table_cell)

    temp_dir = tempfile.gettempdir()
    folder = temp_dir + "/registro-horario/"
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = "Registro_jornada_laboral.odt"
    random_number = str(random.randint(11111, 99999))
    random_filename = random_number + '_' + filename
    random_file_path = temp_dir + "/registro-horario/" + random_filename

    odt_file.save(random_file_path)
    response = send_file(
        random_file_path,
        as_attachment=True,
        download_name=filename)
    os.remove(random_file_path)

    # Enviar el archivo ODT como respuesta
    return response


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/registro_horario_process', methods=['POST'])
def process():
    meses = {
        1: 'ene',
        2: 'feb',
        3: 'mar',
        4: 'abr',
        5: 'may',
        6: 'jun',
        7: 'jul',
        8: 'ago',
        9: 'sep',
        10: 'oct',
        11: 'nov',
        12: 'dic'
    }
    data = request.json

    start_date = datetime.strptime(data.get('start_date'), '%d/%m/%Y')
    end_date = datetime.strptime(data.get('end_date'), '%d/%m/%Y')
    schedule = data.get('schedule', {})
    holidays = data.get('holidays', {})
    unusuals = data.get('unusuals', {})

    total_minutes = 0
    current_date = start_date
    table_sumary = []
    while current_date <= end_date:
        day_of_week = current_date.strftime('%A').lower()

        # Comprobamos si la fecha es un festivo
        current_date_is_holiday = False
        for holiday_range in holidays:
            if is_date_in_range(current_date, holiday_range):
                current_date_is_holiday = True

        if day_of_week in schedule:
            day = current_date.day
            month = meses[current_date.month]
            year = current_date.year
            table_today = [f'{day}/{month}/{year}', [], 0]
            total_minutes_today = 0
            if not current_date_is_holiday:
                for interval in schedule[day_of_week]:
                    entry_time = datetime.strptime(interval['entry'], '%H:%M')
                    exit_time = datetime.strptime(interval['exit'], '%H:%M')
                    formated_entry_time = entry_time.strftime('%-H:%M')
                    formated_exit_time = exit_time.strftime('%-H:%M')
                    table_today[1].append([
                        formated_entry_time,
                        formated_exit_time
                        ])
                    work_minutes = (exit_time - entry_time).seconds / 60
                    total_minutes_today += work_minutes

            for unusual_date in unusuals:
                if unusual_date['date'] == current_date.strftime('%d/%m/%Y'):
                    start_time = unusual_date['start_time']
                    end_time = unusual_date['end_time']
                    entry_time = datetime.strptime(start_time, '%H:%M')
                    exit_time = datetime.strptime(end_time, '%H:%M')
                    table_today[1].append([start_time, end_time])
                    print('start_time: ', start_time)
                    print('entry_time: ', entry_time)
                    print('append: ', entry_time.strftime('%-H:%M'))
                    print('---')
                    work_minutes = (exit_time - entry_time).seconds / 60
                    total_minutes_today += work_minutes

            table_today[2] += round(total_minutes_today, 2)
            total_minutes = round(total_minutes + total_minutes_today, 2)
            if total_minutes_today > 0:
                table_sumary.append(table_today)
        current_date += timedelta(days=1)

    return jsonify(
        {'total_minutes': total_minutes, 'table_sumary': table_sumary}
    )


if __name__ == '__main__':
    # Activar si se ejecuta en local
    # webbrowser.open('http://127.0.0.1:5000/')

    app.run(debug=False)
