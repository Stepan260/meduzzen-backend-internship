from typing import List
from uuid import UUID

from app.repository.result_repository import ResultRepository
from app.schemas.quizzes import UserAverageScoresResponse, UserQuizAverageScoresResponse


async def calculate_user_average_scores_over_time(result_repository: ResultRepository) -> list[
    UserAverageScoresResponse]:
    results = await result_repository.get_many(skip=1, limit=1000)

    user_average_scores_over_time = {}

    for result in results:
        user_uuid = result.user_uuid
        score = result.score
        created_at = result.created_at

        date_period = created_at.date()

        if user_uuid not in user_average_scores_over_time:
            user_average_scores_over_time[user_uuid] = {}

        if date_period not in user_average_scores_over_time[user_uuid]:
            user_average_scores_over_time[user_uuid][date_period] = []

        user_average_scores_over_time[user_uuid][date_period].append(score)

    user_average_scores_list = []

    for user_uuid, date_scores in user_average_scores_over_time.items():
        for date_period, scores in date_scores.items():
            average_score = sum(scores) / len(scores)

            user_average_score = UserAverageScoresResponse(
                user_uuid=user_uuid,
                date_period=date_period,
                average_score=average_score
            )

            user_average_scores_list.append(user_average_score)

    return user_average_scores_list


async def calculate_user_quiz_average_scores_over_time(
        result_repository: ResultRepository,
        user_uuid: UUID
) -> List[UserQuizAverageScoresResponse]:
    results = await result_repository.get_many(user_uuid=user_uuid, skip=1, limit=1000)

    quiz_average_scores_over_time = {}

    for result in results:
        quiz_uuid = result.quiz_uuid
        score = result.score
        created_at = result.created_at

        date_period = created_at.date()

        if quiz_uuid not in quiz_average_scores_over_time:
            quiz_average_scores_over_time[quiz_uuid] = {}

        if date_period not in quiz_average_scores_over_time[quiz_uuid]:
            quiz_average_scores_over_time[quiz_uuid][date_period] = []

        quiz_average_scores_over_time[quiz_uuid][date_period].append(score)

    quiz_average_scores_list = []

    for quiz_uuid, date_scores in quiz_average_scores_over_time.items():
        for date_period, scores in date_scores.items():
            average_score = sum(scores) / len(scores)

            quiz_average_score = UserQuizAverageScoresResponse(
                quiz_uuid=quiz_uuid,
                date_period=date_period,
                average_score=average_score
            )

            quiz_average_scores_list.append(quiz_average_score)

    return quiz_average_scores_list
