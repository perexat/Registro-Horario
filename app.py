from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

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
    #data = {'start_date': '01/06/2024', 'end_date': '30/06/2024', 'schedule': {'monday': [{'entry': '08:00', 'exit': '09:00'}], 'tuesday': [{'entry': '08:00', 'exit': '10:00'}], 'wednesday': [{'entry': '08:00', 'exit': '09:00'}, {'entry': '11:00', 'exit': '12:00'}], 'thursday': [{'entry': '08:00', 'exit': '09:30'}], 'friday': [{'entry': '09:30', 'exit': '11:00'}]}, 'unusuals': [{'date': '05/06/2024', 'start_time': '15:00', 'end_time': '16:30'}, {'date': '12/06/2024', 'start_time': '15:00', 'end_time': '18:00'}], 'holidays': [['17/06/2024', '18/06/2024'], ['25/06/2024', '30/06/2024']]}

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


    total_hours = 0
    current_date = start_date
    table_sumary = []
    while current_date <= end_date:
        day_of_week = current_date.strftime('%A').lower()

        current_date_is_holiday = False #Comprobamos si la fecha es un festivo
        for holiday_range in holidays:
            if is_date_in_range(current_date, holiday_range):
                current_date_is_holiday = True

        if day_of_week in schedule and not current_date_is_holiday:
            table_today = [f'{current_date.day}/{meses[current_date.month]}/{current_date.year}',[],0]
            total_hours_today = 0
            for interval in schedule[day_of_week]:
                entry_time = datetime.strptime(interval['entry'], '%H:%M')
                exit_time = datetime.strptime(interval['exit'], '%H:%M')
                table_today[1].append([entry_time.strftime('%-H:%M'),exit_time.strftime('%-H:%M')])
                work_hours = round((exit_time - entry_time).seconds / 3600, 2)
                total_hours_today += work_hours


            for unusual_date in unusuals:
                if unusual_date['date'] == current_date.strftime('%d/%m/%Y'):
                    # print('Coincidencia comparando {0} con {1}'.format(unusual_date['date'], current_date.strftime('%d/%m/%Y'))),
                    entry_time = datetime.strptime(unusual_date['start_time'], '%H:%M')
                    exit_time = datetime.strptime(unusual_date['end_time'], '%H:%M')
                    table_today[1].append([entry_time.strftime('%-H:%M'),exit_time.strftime('%-H:%M')])
                    work_hours = round((exit_time - entry_time).seconds / 3600, 2)
                    total_hours_today += work_hours




            table_today[2] += total_hours_today
            total_hours += total_hours_today
            if total_hours_today > 0:
                table_sumary.append(table_today)
        current_date += timedelta(days=1)
    table_sumary.append(['Total de horas trabajadas en el período: ',[],total_hours])


    '''print('TABLA RESUMEN')
    print(table_sumary)
    for day in table_sumary:
        print(day[0])
        for interval in day[1]:
            print(f'     {interval[0]} - {interval[1]}')
        print('Total del dia: ', f'{int((day[2] * 60) // 60)}:{int((day[2] * 60) % 60)}')
    print(table_sumary)'''

    return jsonify(table_sumary)

if __name__ == '__main__':
    app.run(debug=True)
