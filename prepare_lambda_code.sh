#!/bin/bash

rm lambda_code.zip
cd lambda_code
cp ../ChallengeTestRunner/challenge_test_lib/challenge_test.py challenge_test_lib/challenge_test.py
zip -r9 ../lambda_code.zip .
cd ..