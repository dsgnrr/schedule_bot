import json

class Lesson:
    def __init__(this, name, teacher_name, start_time, end_time,date, zref) -> None:
        this.name = name
        this.teacher_name = teacher_name
        this.date = date
        this.start_time = start_time
        this.end_time = end_time
        this.zref = zref
    def __str__(this) -> str:
        return f"⏰ {this.start_time}-{this.end_time}\n👨‍🏫 {this.teacher_name}\n📚 {this.name}\n🔗 {this.zref}"
    