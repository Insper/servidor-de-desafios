import json

objects = []
with open('raw.txt') as file:
    test_pk = 1
    for line in file:
        elements = line.strip().split('|')
        challenge_id, release, expire, problem, tests, results, diagnosis = elements
        challenge_id = int(challenge_id)
        tests = eval(tests)
        results = eval(results)
        diagnosis = eval(diagnosis)
        challenge = {
            "model": "core.Challenge",
            "pk": challenge_id,
            "fields": {
                "release": release,
                "expire": expire,
                "problem": problem,
            }
        }
        objects.append(challenge)
        for t, r, d in zip(tests, results, diagnosis):
            test = {
                "model": "core.Test",
                "pk": test_pk,
                "fields": {
                    "challenge": challenge_id,
                    "test": str(t),
                    "result": str(r),
                    "diagnosis": str(d),
                }
            }
            objects.append(test)
            test_pk += 1

with open('initial_data.json', 'w') as file:
    json.dump(objects, file)
