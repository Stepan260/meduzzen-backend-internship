import json
import csv
import tempfile
from fastapi.responses import FileResponse

from app.db.redisdb import redis_connection
from fastapi import HTTPException


async def redis_file_content(query: str, file_format: str) -> FileResponse:
    keys = await redis_connection.keys(query)
    data = []

    for key in keys:
        redis_value = await redis_connection.get(key)
        print(json.loads(redis_value))
        data.append(json.loads(redis_value))

    if file_format == 'json':
        temp_json_file = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json')
        json.dump(data, temp_json_file, indent=2)
        temp_json_file.close()

        return FileResponse(temp_json_file.name, filename='quiz_results.json')

    elif file_format == 'csv':
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv') as temp_csv_file:
            fieldnames = ['user_uuid', 'company_uuid', 'quiz_uuid', 'question_uuid', 'user_answer', 'is_correct']
            writer = csv.DictWriter(temp_csv_file, fieldnames=fieldnames)
            writer.writeheader()

            for item in data:
                user_uuid = item.get('user_uuid')
                company_uuid = item.get('company_uuid')
                quiz_uuid = item.get('quiz_uuid')
                questions = item.get('questions', [])

                for question_data in questions:
                    question_uuid = question_data.get('question_uuid')
                    user_answer = question_data.get('user_answer')
                    is_correct = question_data.get('is_correct')

                    writer.writerow({
                        'user_uuid': user_uuid,
                        'company_uuid': company_uuid,
                        'quiz_uuid': quiz_uuid,
                        'question_uuid': question_uuid,
                        'user_answer': user_answer,
                        'is_correct': is_correct,
                    })

            return FileResponse(temp_csv_file.name, filename='quiz_results.csv')
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")
