from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler

from django.contrib.auth.models import User
from challenges.models import *
from .models import *


def __fetch_or_create_challenge_reports(users, challenges):
    all_reports = {(r.user.id, r.challenge.id): r for r in UserChallengeReport.objects.all()}
    for user in users:
        for challenge in challenges:
            key = (user.id, challenge.id)
            if key not in all_reports:
                all_reports[key] = UserChallengeReport(user=user, challenge=challenge)
                all_reports[key].save()
            all_reports[key].attempts = 0
            all_reports[key].best_result = str(Result.ERROR)
    return all_reports


def update():
    users = User.objects.all()
    user_submissions = ChallengeSubmission.objects.all()
    challenges = Challenge.all_published()

    challenge_reports = __fetch_or_create_challenge_reports(users, challenges)

    for sub in user_submissions:
        report = challenge_reports[(sub.author.id, sub.challenge.id)]
        report.attempts += 1
        if sub.result == str(Result.OK):
            report.best_result = str(Result.OK)

    for report in challenge_reports.values():
        report.save()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update, 'cron', hour=3, minute=7)
    scheduler.start()
