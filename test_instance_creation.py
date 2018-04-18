import connections
bc3_conn = connections.Bc3('oc13378', 'bc3', 'test_forename', 'test_surname', 'test_email', '/test/output/path', '/test/runfiles/path', 'This is an imaginary cluster, created for testing' )
bc3_conn.createWcmKoScript('test_job_name', 'test_submission_script.sh', '/test/wcm/master', '/test/output', '/test/outfiles', '/test/errorfiles', '/test/ko/codes.txt', '/test/ko/dir_names.txt', 1000, 3)
