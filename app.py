from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

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
    start_date = datetime.strptime(data.get('start_date'), '%d/%m/%Y')
    end_date = datetime.strptime(data.get('end_date'), '%d/%m/%Y')
    schedule = data.get('schedule', {})


    ###################### Depuración #####
    print('DATA:')
    print(data)
    print('-----')
    print('SCHEDULE:')
    print(schedule)
    print('-----')
    holidays = data.get('holidays', {})
    print('HOLIDAYS:')
    print(holidays)
    print('-----')
    unusuals = data.get('unusuals', {})
    print('UNUSUALS:')
    print(unusuals)




    total_hours = 0
    current_date = start_date
    table_sumary = []
    while current_date <= end_date:
        day_of_week = current_date.strftime('%A').lower()
        if day_of_week in schedule:
            table_today = [f'{current_date.day}/{meses[current_date.month]}/{current_date.year}',[],0]
            total_hours_today = 0
            for interval in schedule[day_of_week]:
                entry_time = datetime.strptime(interval['entry'], '%H:%M')
                exit_time = datetime.strptime(interval['exit'], '%H:%M')
                table_today[1].append([entry_time.strftime('%-H:%M'),exit_time.strftime('%-H:%M')])
                work_hours = (exit_time - entry_time).seconds / 3600
                total_hours_today += work_hours
            table_today[2] += total_hours_today
            total_hours += total_hours_today
            table_sumary.append(table_today)
        current_date += timedelta(days=1)
    for day in table_sumary:
        print(day[0])
        for interval in day[1]:
            print(f'     {interval[0]} - {interval[1]}')
        print('Total del dia: ', f'{int((day[2] * 60) // 60)}:{int((day[2] * 60) % 60)}')

    return jsonify({'total_hours': total_hours})

if __name__ == '__main__':
    app.run(debug=True)
