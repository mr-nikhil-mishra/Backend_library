from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId

#Information related to database can be kept in private but in task it was not mention so added in main file only

client = MongoClient("mongodb+srv://parth01:parth123@cluster0.77are8z.mongodb.net/?retryWrites=true&w=majority")
db = client["Library"]
collection = db["students"]

app = FastAPI()

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

@app.post("/students/", status_code=201, tags=["Students"])
def create_student(student: Student):
    """
    Create Students
    API to create a student in the system. All fields are mandatory and required while creating the student in the system.
    """
    student_dict = student.dict()
    result = collection.insert_one(student_dict)
    return {"id": str(result.inserted_id)}

@app.get("/students/", response_model=dict, tags=["Students"])
def list_students(country: str = None, age: int = None):
    """
    List students
    An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below.
    """
    query = {}
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}
    students = list(collection.find(query, {"_id": 0}))
    return {"data": students}

@app.get("/students/{student_id}", response_model=Student, tags=["Students"])
def get_student(student_id: str):
    """
    Fetch student
    """
    student = collection.find_one({"_id": ObjectId(student_id)}, {"_id": 0})
    if student:
        return student
    else:
        raise HTTPException(status_code=404, detail="Student not found")

@app.patch("/students/{student_id}", status_code=204, tags=["Students"])
def update_student(student_id: str, student: Student):
    """
    Update student
    API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database.
    """
    student_dict = student.dict(exclude_unset=True)  # exclude_unset ensures only provided fields are updated
    result = collection.update_one({"_id": ObjectId(student_id)}, {"$set": student_dict})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}", tags=["Students"])
def delete_student(student_id: str):
    """
    Delete student
    """
    result = collection.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"id": student_id}
