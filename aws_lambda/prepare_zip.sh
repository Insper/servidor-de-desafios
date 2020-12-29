rm str_test_lambda.zip
cd str_test_lambda
zip -r ../str_test_lambda.zip *
cd ..

rm mem_test_lambda.zip
cd mem_test_lambda
cp ../../trace_challenge/memory_compare.py trace_challenge/
cp ../../trace_challenge/error_code.py trace_challenge/
zip -r ../mem_test_lambda.zip *
cd ..
