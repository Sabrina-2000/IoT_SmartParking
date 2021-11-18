from flask import Flask, render_template, request
import MySQLdb
app = Flask(__name__, template_folder="templates")
available = 3
count = 0
slots = ["-", "-","-"]
status = "Book Failed"


@app.route("/")
def index():
    dbConn = MySQLdb.connect("localhost","pi","","parkingSystem_db") or dle("Could not connect to database") 
    print(dbConn)
    with dbConn:
        cursor = dbConn.cursor()
        cursor.execute("SELECT * FROM record")
        dbConn.commit()
        for Id, Counts, Availables, SlotA1, SlotA2, SlotB1 in cursor:
            count = int(Counts)
            available = int(Availables)
            slots[0] = SlotA1
            slots[1] = SlotA2
            slots[2] = SlotB1
        cursor.close()
        
    displaySlot = []
    if(slots[0] == "-"):
        displaySlot.append("A1")
    if(slots[1] == "-"):
        displaySlot.append("A2")
    return render_template('index.html', available=available, count=count, displaySlot=displaySlot)

@app.route("/", methods=['POST'])
def getBooking():
    global status, count, available
    name = request.form['name']
    phone = request.form['phone']
    slotNum = request.form['slotNum']
    plate = request.form['plate']
    if(slotNum.upper() == "A1"):
        slots[0] = plate + "@"
        status = "Successfully Booked"
        count += 1
        available -= 1
    elif(slotNum.upper() == "A2"):
        slots[1] = plate + "@"
        status = "Successfully Booked"
        count += 1
        available -= 1
    
    dbConn = MySQLdb.connect("localhost","pi","","parkingSystem_db") or dle("Could not connect to database") 
    print(dbConn)
    with dbConn:
        cursor = dbConn.cursor()
        cursor.execute("INSERT INTO record (Counts, Availables, SlotA1, SlotA2, SlotB1) VALUES ('%s','%s','%s','%s','%s')" %(count, available, slots[0], slots[1], slots[2])) 
        dbConn.commit()
        cursor.close()
    
    return render_template('bookInfo.html', name=name, phone=phone, slotNum=slotNum, plate=plate, status=status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 


