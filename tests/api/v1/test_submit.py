from .base import BaseAPITest
import os
import pprint
import time


class SubmitTest(BaseAPITest):
    def test_submit_small_job(self):
        callback_server = self.create_callback_server([200])

        test_data = 'hello small job'
        outfile = self.make_tempfile()
        submit_data = {
            'command': 'echo "%s"' % test_data,
            'options': {
                'outFile': outfile,
            },
            'rLimits': {
                'cpuTime': 1,
            },
            'webhooks': {
                'error': callback_server.url,
                'failure': callback_server.url,
                'success': callback_server.url,
            },
        }
        self.set_queue(submit_data)

        response = self.post(self.jobs_url, submit_data)
        self.print_response(response)

        self.assertEqual(response.status_code, 201)

        time.sleep(5)

        status_response = self.get(response.headers['Location'])
        self.assertEqual(status_response.status_code, 200)

        self.print_response(status_response)

        webhook_data = callback_server.stop()
        pprint.pprint(webhook_data)

        data = open(outfile).read()
        self.assertRegexpMatches(data, '%s.*' % test_data)

        status_response = self.get(response.headers['Location'])
        self.assertEqual(status_response.status_code, 200)

        self.print_response(status_response)

        for key, value in submit_data.iteritems():
            self.assertEqual(status_response.DATA[key], value)

        self.assertIsInstance(status_response.DATA['lsfJobId'], int)