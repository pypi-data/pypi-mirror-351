from supabase import create_client, PostgrestAPIResponse
from dotenv import load_dotenv
from datetime import date
from pathlib import Path
import os

print(Path.cwd())
load_dotenv(dotenv_path=Path.cwd() / ".env")
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise Exception("Missing required environment variables: SUPABASE_URL and SUPABASE_KEY")
supabase = create_client(url, key)

def create_user(name: str, email:str, **extra_fields) -> PostgrestAPIResponse:
    '''
    To create a new user. (Inside `users` table)
    
    eg:
    create_user("Hadin Abdul Hameed", "hadinabdulhameed@gmail.com")
    '''
    data = {
        "name": name,
        "email": email,
        **extra_fields
    }

    response = supabase.table("users").insert(data).execute()
    return response.data

def start_workday(notes: str='regular', **extra_fields) -> PostgrestAPIResponse:
    '''
    To start workday. (Inside `workdays` table)

    eg:
    start_workday()
    '''
    data = {
        "notes": notes,
        **extra_fields
    }

    response = supabase.table("workdays").insert(data).execute()
    return response.data

def stop_workday(notes: str='regular', **extra_fields) -> PostgrestAPIResponse:
    '''
    To stop workday. (Inside `workdays` table)

    eg:
    stop_workday()
    '''
    data = {
        "notes": notes,
        **extra_fields
    }

    response = supabase.table("workdays").update(data).eq("workday_id", str(date.today())).execute()
    return response.data

def mark_entry(user_id: str, **extra_fields) -> PostgrestAPIResponse:
    '''
    To mark the entry of user. (Inside `entry_logs` table, with `entry=True`)

    eg:
    mark_entry("aad1a0aa-dea4-a1ae-4a1a-aaeaaaa10aaa")
    '''
    data = {
        "user_id": user_id,
        "entry": True,
    }

    response = supabase.table("entry_logs").insert(data).execute()
    return response.data

def mark_exit(user_id: str, **extra_fields) -> PostgrestAPIResponse:
    '''
    To mark the exit of the user. (Inside `entry_logs`, with `entry=False`)

    eg:
    mark_exit("aad1a0aa-dea4-a1ae-4a1a-aaeaaaa10aaa")
    '''
    data = {
        "user_id": user_id,
        "entry": False,
        **extra_fields
    }

    response = supabase.table("entry_logs").insert(data).execute()
    return response.data

def mark_task(user_id: str, task: str, tags: str="", **extra_fields) -> PostgrestAPIResponse:
    '''
    To mark task, which is done. (Inside `task_logs`)

    eg:
    mark_task("aad1a0aa-dea4-a1ae-4a1a-aaeaaaa10aaa", "Made Database", "{databse, sql, python}")
    '''
    data = {
        "name": task,
        "user_id": user_id,
        "tags": tags,
        **extra_fields
    }

    response = supabase.table("task_logs").insert(data).execute()
    return response.data

def get_table_datas(table_name: str, **filters) -> PostgrestAPIResponse:
    '''
    To get datas of any table, where key=value.

    eg:
    get_table_datas('users', name="Hadin Abdul Hameed")
    '''
    query = supabase.table(table_name).select("*")
    for key, value in filters.items():
        query = query.eq(key, value)
    return query.execute()

def get_users(user_id: str="*", name: str="*", email: str="*", operator: str="", **extra_fields) -> PostgrestAPIResponse:
    '''
    To get datas inside `users` table, where key=value(if any).
    
    eg:
    get_users(email="hadinabdulhameed@gmail.com")
    '''
    query = supabase.table("users").select("*")

    if user_id != "*":
        query = query.eq("user_id", user_id)
    if name != "*":
        query = query.eq("name", name)
    if email != "*":
        query = query.eq("email", email)
        query.cd
    #for key, item in extra_fields

    response = query.execute()
    return response.data

def get_workday(workday_id: str="*", notes: str="*", opening_time: str="*", closing_time: str="*") -> PostgrestAPIResponse:
    '''
    To get datas inside `workdays` table, where key=value(if any).
    
    eg:
    get_workday(notes="regular")
    '''
    query = supabase.table("workdays").select("*")

    if workday_id != "*":
        query = query.eq("workday_id", workday_id)
    if notes != "*":
        query = query.eq("notes", notes)
    if opening_time != "*":
        query = query.eq("opening_time", opening_time)
    if closing_time != "*":
        query = query.eq("closing_time", closing_time)

    response = query.execute()
    return response.data

def get_entry(entry_id: str="*", workday_id: str="*", user_id: str="*") -> PostgrestAPIResponse:
    '''
    To get datas inside `entry_logs` table, where key=value(if any) (With `entry`=False).
    
    eg:
    get_entry(workday_id="2025-04-17")
    '''
    query = supabase.table("entry_logs").select("*").eq("entry", True)

    if entry_id != "*":
        query = query.eq("entry_id", entry_id)
    if workday_id != "*":
        query = query.eq("workday_id", workday_id)
    if user_id != "*":
        query = query.eq("user_id", user_id)

    response = query.execute()
    return response.data

def get_exits(entry_id: str="*", workday_id: str="*", user_id: str="*") -> PostgrestAPIResponse:
    '''
    To get datas inside `entry_logs` table, where key=value(if any) (With `entry`=False).
    
    eg:
    get_exits(user_id="aad1a0aa-dea4-a1ae-4a1a-aaeaaaa10aaa", workday_id="2025-04-17")
    '''
    query = supabase.table("entry_logs").select("*").eq("entry", False)

    if entry_id != "*":
        query = query.eq("entry_id", entry_id)
    if workday_id != "*":
        query = query.eq("workday_id", workday_id)
    if user_id != "*":
        query = query.eq("user_id", user_id)

    response = query.execute()
    return response.data

def get_tasks(id: str="*", workday_id: str="*", user_id: str="*", tags: dict=[], name: str="*") -> PostgrestAPIResponse:
    '''
    To get datas inside `task_logs` table, where key=value(if any).
    
    eg:
    get_tasks(workday_id="2025-04-1.7", tags=["python"])
    '''
    query = supabase.table("task_logs").select("*")

    if id != "*":
        query = query.eq("id", id)
    if workday_id != "*":
        query = query.eq("workday_id", workday_id)
    if user_id != "*":
        query = query.eq("user_id", user_id)
    if tags != []:
        query = query.contains("tags", tags)
    if name != "*":
        query = query.eq("name", name)
    

    response = query.execute()
    return response.data

__all__ = ["create_user", "start_workday", "stop_workday", "mark_entry",
           "mark_exit", "mark_task", "get_table_datas", "get_users", "get_workday",
           "get_entry", "get_exits", "get_tasks"]
if __name__ == "__main__":
    print(create_user(name="Hadin Abdul Hameed", email="hadinabdulhameed@gmail.com", discord_id="1087016840737341581"))