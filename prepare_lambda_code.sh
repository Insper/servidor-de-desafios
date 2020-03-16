#!/bin/bash

rm lambda_code.zip
cd lambda_code
cp ../ChallengeTestRunner/challenge_test_lib/*.py challenge_test_lib/
zip -r9 ../lambda_code.zip .
cd ..
