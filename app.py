from flask import Flask, request, jsonify, render_template, send_file
from datetime import datetime, timedelta
from odf.opendocument import OpenDocumentText
from odf.text import P, H
from odf.table import Table, TableRow, TableCell, TableColumn
from odf.style import Style, TextProperties, TableColumnProperties, TableRowProperties, TableCellProperties
import re, webbrowser, json

app = Flask(__name__)

CLEANR = re.compile('<.*?>')

def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext

def is_date_in_range(date_str, date_range):
    # Convertir la fecha y el rango de fechas de strings a objetos datetime
    #date = datetime.strptime(date_str, '%d/%m/%Y')
    start_date = datetime.strptime(date_range[0], '%d/%m/%Y')
    if date_range[1] != None:
        end_date = datetime.strptime(date_range[1], '%d/%m/%Y')
    else:
        end_date = start_date

    # Verificar si la fecha está en el rango
    return start_date <= date_str <= end_date

@app.route('/subir_datos', methods=['POST'])
def subir_datos():
    contenido = request.data.decode('utf-8')  # Obtener el contenido del archivo enviado desde el frontend
    print('-')
    return contenido
    #return jsonify(contenido)

@app.route('/descargar_formulario', methods=['POST'])
def descargar_datos_formulario():
    data = request.get_json()

    # Guardar los datos JSON en un archivo de texto
    with open("/tmp/datos_formulario.txt", "w") as file:
        json.dump(data, file)

    # Enviar el archivo de texto como respuesta para descargar
    return send_file("/tmp/datos_formulario.txt", as_attachment=True)


@app.route('/descargar_tabla_odt', methods=['POST'])
def descargar_tabla_odt():
    data = request.get_json()
    table_html = data.get('tableHtml', '')
    name = data.get('name', '')
    empresa = data.get('empresa', '')
    horascontrato = data.get('horascontrato', '')
    date_range = str(data.get('daterange', ''))
    total_hours = str(data.get('totalhours', ''))


    # Crear un archivo ODT con la tabla de tres columnas
    odt_file = OpenDocumentText()

    # Crear un estilo de texto con color azul
    style1 = Style(name="style1", family="paragraph")
    style1_props = TextProperties(fontweight="bold", fontsize="18pt", color="#FFFFFF", backgroundcolor="#3465A4")
    style1.addElement(style1_props)

    # Crear un estilo de texto con color azul
    style2 = Style(name="style2", family="paragraph")
    style2_props = TextProperties(fontweight="bold", fontsize="12pt", color="#3465A4")
    style2.addElement(style2_props)

    # Agregar el estilo al documento
    odt_file.automaticstyles.addElement(style2)
    odt_file.automaticstyles.addElement(style1)


    # Crear un estilo para la cabecera de la tabla
    header_style = Style(name="HeaderStyle", family="table-cell")
    header_cell_props = TableCellProperties(backgroundcolor="#b4c7dc", border="0.5pt solid #000000")
    header_style.addElement(header_cell_props)

    # Agregar el estilo al documento
    odt_file.automaticstyles.addElement(header_style)

    # Crear un estilo para el cuerpo de la tabla
    body_style = Style(name="BodyStyle", family="table-cell")
    body_cell_props = TableCellProperties(backgroundcolor="#FFFFFF", border="0.5pt solid #000000")
    body_style.addElement(body_cell_props)

    # Agregar el estilo al documento
    odt_file.automaticstyles.addElement(header_style)


    odt_file.text.addElement(H(outlinelevel=4, stylename=style1, text="Nombre: " + name))
    odt_file.text.addElement(H(outlinelevel=4, stylename=style2, text="Empresa: " + empresa))
    odt_file.text.addElement(H(outlinelevel=4, stylename=style2, text="Horas según contrato: " + horascontrato))
    odt_file.text.addElement(H(outlinelevel=4, stylename=style2, text="Rango de fechas: " + date_range))

    table = Table()

    odt_file.text.addElement(table)

    for i in range(3):
        table_column = TableColumn()
        table.addElement(table_column)

    # Parsear el contenido HTML de la tabla y agregarlo a la tabla en el documento ODT
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
                        #cell_content = cell.replace('<td>', '').strip()
                        cell = cell.replace("<br>", "//")
                        cell_content = cleanhtml(cell)
                        if table_section == thead:
                            table_cell = TableCell(stylename=header_style)
                        else:
                            table_cell = TableCell(stylename=body_style)
                        for line in cell_content.split('//'):
                            paragraph = P(text=line)
                            table_cell.addElement(paragraph)
                        #table_cell.addElement(P(text=cell_content))
                        table_row.addElement(table_cell)



    # Añadir celdas vacías si es necesario para completar las tres columnas en cada fila
    for row in table.getElementsByType(TableRow):
        while len(row.getElementsByType(TableCell)) < 3:
            table_cell = TableCell()
            table_cell.addElement(P(text=''))
            row.addElement(table_cell)

    # Sumamos el contenido de todas las celdas de la tercera columnas
    ''' No es necesario, recibimos el total de horas ya calculado
    total_hours = 0
    saltar_primera_linea = True
    for row in table.getElementsByType(TableRow):
        cells = row.getElementsByType(TableCell)
        if len(cells) >= 3:  # Verificar que la fila tenga al menos 3 celdas
            cell_content = cells[2].firstChild
            if cell_content is not None and not saltar_primera_linea:
                total_hours += float(cell_content.firstChild.data)
        saltar_primera_linea = False
    '''

    odt_file.text.addElement(H(outlinelevel=4, text="Horas totales: " + str(total_hours)))

    odt_file.save("/tmp/Registro_jornada_laboral.odt")

    # Enviar el archivo ODT como respuesta
    return send_file("/tmp/Registro_jornada_laboral.odt", as_attachment=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
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

    # Datos de prueba
    #data = {'start_date': '01/06/2024', 'end_date': '30/06/2024', 'schedule': {'monday': [{'entry': '08:08', 'exit': '09:09'}], 'tuesday': [{'entry': '08:08', 'exit': '09:09'}, {'entry': '10:00', 'exit': '11:11'}], 'wednesday': [{'entry': '08:08', 'exit': '10:01'}], 'thursday': [], 'friday': [{'entry': '08:00', 'exit': '09:00'}]}, 'unusuals': [{'date': '04/06/2024', 'start_time': '15:00', 'end_time': '18:00'}, {'date': '07/06/2024', 'start_time': '15:00', 'end_time': '19:00'}], 'holidays': [['19/06/2024', '23/06/2024']]}

    start_date = datetime.strptime(data.get('start_date'), '%d/%m/%Y')
    end_date = datetime.strptime(data.get('end_date'), '%d/%m/%Y')
    schedule = data.get('schedule', {})
    holidays = data.get('holidays', {})
    unusuals = data.get('unusuals', {})



    ###################### Depuración #####
    #print('DATA:')
    #print(data)
    #print('-----')
    #print('SCHEDULE:')
    #print(schedule)
    #print('-----')

    #print('HOLIDAYS:')
    #print(holidays)
    #print('-----')

    #print('UNUSUALS:')
    #print(unusuals)


    total_minutes = 0
    current_date = start_date
    table_sumary = []
    while current_date <= end_date:
        day_of_week = current_date.strftime('%A').lower()

        current_date_is_holiday = False #Comprobamos si la fecha es un festivo
        for holiday_range in holidays:
            if is_date_in_range(current_date, holiday_range):
                current_date_is_holiday = True

        if day_of_week in schedule:
            table_today = [f'{current_date.day}/{meses[current_date.month]}/{current_date.year}',[],0]
            total_minutes_today = 0
            if  not current_date_is_holiday:
                for interval in schedule[day_of_week]:
                    entry_time = datetime.strptime(interval['entry'], '%H:%M')
                    exit_time = datetime.strptime(interval['exit'], '%H:%M')
                    table_today[1].append([entry_time.strftime('%-H:%M'),exit_time.strftime('%-H:%M')])
                    work_minutes = (exit_time - entry_time).seconds / 60
                    total_minutes_today += work_minutes


            for unusual_date in unusuals:
                if unusual_date['date'] == current_date.strftime('%d/%m/%Y'):
                    # print('Coincidencia comparando {0} con {1}'.format(unusual_date['date'], current_date.strftime('%d/%m/%Y'))),
                    entry_time = datetime.strptime(unusual_date['start_time'], '%H:%M')
                    exit_time = datetime.strptime(unusual_date['end_time'], '%H:%M')
                    table_today[1].append([entry_time.strftime('%-H:%M'),exit_time.strftime('%-H:%M')])
                    work_minutes = (exit_time - entry_time).seconds / 60
                    total_minutes_today += work_minutes




            table_today[2] += round(total_minutes_today, 2)
            total_minutes = round(total_minutes + total_minutes_today, 2)
            if total_minutes_today > 0:
                table_sumary.append(table_today)
        current_date += timedelta(days=1)
    #table_sumary.append(['Total de horas trabajadas en el período: ',[],round(total_minutes, 2)])


    '''print('TABLA RESUMEN')
    print(table_sumary)
    for day in table_sumary:
        print(day[0])
        for interval in day[1]:
            print(f'     {interval[0]} - {interval[1]}')
        print('Total del dia: ', f'{int((day[2] * 60) // 60)}:{int((day[2] * 60) % 60)}')
    print(table_sumary)'''

    return jsonify({'total_minutes': total_minutes, 'table_sumary':table_sumary})

if __name__ == '__main__':
    # Activar si se ejecuta en local
    webbrowser.open('http://127.0.0.1:5000/')

    app.run(debug=False)
