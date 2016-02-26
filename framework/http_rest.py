import sys, json
from getpass import getpass
import requests
# from requests import *
import requests.exceptions
import logging
import logging.config
from time import sleep
import configparser
from framework.constants import *
from framework.authentication_rest import get_auth_token
import traceback


def rest_request(session, type_of_call, baseurl="", apiurl="", query_params=None, payload_params=None, file_object=None,
                 headers=None, proxy=False):
    '''
    Makes an HTTP request into the passed seession object.  The URL used for the request can be found by
    concatenating baseurl and apiurl.  For example:

    baseurl = 'http://<some CM IP>:<some CM upd port>/ContentManager'
    apiurl = '/api/rest/<some api location>'

    This method will call:

    'http://<some CM IP>:<some CM upd port>/ContentManager/api/rest/<some api location>

    Parameters are defined by the 'params' parameter.  If type_of_call is 'get,' parameters are passed in
    the url as query parameters.  For all other values of type_of_call, the parameters are encoded JSON objects
    in the body of the HTTP request.

    :param session: A logged in requests.session object
    :param type_of_call: framework.constants enumeration of valid http call type (put/get/post etc.)
    :param baseurl: String containing the url of the CM under test.  Usually configured in config/testconfig
    :param apiurl:  The second part of the URL for this call - specific to the REsT request being made
    :param query_params: Dictionary containing the parameters passed in the URL for this call
    :param payload_params: Dictionary containing the JSON represented payload parameters for this call parameters for this call.
    :param proxy: Set to true to use a proxy server when sending the call.  Use when debugging using a sniffing Proxy (Unsupported)
    :param file_object: File like object for use in file uploads etc.
    :param headers: A Dictionary containing the custom headers to be added to the HTTP request
    :returns:  response object representing the call
    :raises: Connection Error if the connection to the server could not be validated
    :raises: HTTPError if an HTTP error occurs
    :raises: URLRequired Error if the URL is not valid
    :raises: TooManyRedirects Error if too many redirects occur
    '''

    authurl = baseurl + apiurl
    logging.debug('Entering rest_request to issue http request to CM.')
    logging.info('url request is: ' + str(authurl))
    logging.info('payload parameters to send are: ' + str(payload_params))
    logging.info('query parameters to send are: {}'.format(query_params))
    logging.info('Type of HTTP request is: ' + type_of_call.name)
    logging.info('File object used in request is: {}'.format(file_object))
    logging.info('Headers specified for this request is: {}'.format(headers))

    # Add hooks for logging performance data
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    use_compression = config['compression']['isCompressedRequests']
    # perf_logger = logging.getLogger('performance')
    # perf_logger.setLevel(logging.INFO)
    # # perf_log_handler = logging.FileHandler(config['logging']['perf_log_path'])
    # perf_log_handler = logging.FileHandler(PERF_LOG_FILE_PATH,mode='w')
    # perf_log_handler.setLevel(logging.NOTSET)
    # perf_log_formatter = logging.Formatter('%(asctime)s - %(message)s')
    # perf_log_handler.setFormatter(perf_log_formatter)
    # logger.addHandler(perf_log_handler)


    data = None

    # requests library does not support using both a file as a data parameter AND a file like object.

    data = file_object

    if payload_params is not None and file_object is not None:
        logging.error(
            'Framework cannot make a request which has both a file upload and payload parameters at this time.')
        raise ValueError('Cannot process rest request because the payload is both a file type and JSON')
    if file_object is None:
        data = json.dumps(payload_params)

    if use_compression == 'True':
        if headers==None:
            headers = {}
        headers['Accept-Encoding'] = 'gzip, deflate'

    try:
#        logging.debug(
#            'The authorization token on the session JUST before I send the get request is: ' + get_auth_token(session))
        if type_of_call is call_type.get:
            resp = session.get(authurl, params=query_params, data=data, proxies=None, timeout=DEFAULT_HTTP_TIMEOUT)
        elif type_of_call is call_type.put:
            resp = session.put(authurl, params=query_params, data=data, headers=headers, proxies=None,
                               timeout=DEFAULT_HTTP_TIMEOUT)
        elif type_of_call is call_type.post:
            resp = session.post(authurl, params=query_params, data=data, headers=headers, proxies=None,
                                timeout=DEFAULT_HTTP_TIMEOUT)
        elif type_of_call is call_type.delete:
            resp = session.delete(authurl, params=query_params, data=data, headers=headers, files=file_object,
                                  proxies=None, timeout=DEFAULT_HTTP_TIMEOUT)
        else:
            logging.error('Could not determine the type of http call to make')
            raise ValueError('Invalid type of http request: %r' % type_of_call.name)
        logging.info('Http response code for session request is: ' + str(resp.status_code))
        logging.info(
            'PERFORMANCE: Call to {} {} took {} seconds '.format(type_of_call.name, authurl, str(resp.elapsed)))
        #perf_logger.info('PERFORMANCE: Call to {} {} took {} seconds '.format(type_of_call.name, authurl, str(resp.elapsed)))
        #perf_logger.info('PERFORMANCE: Call to {} {} took {} seconds '.format(type_of_call.name, authurl, str(resp.elapsed)))
        return resp
    except requests.exceptions.ConnectionError:
        logging.error('A Connection error occurred.')
    except requests.exceptions.HTTPError:
        logging.error('An HTTP error occurred.')
    except requests.exceptions.URLRequired:
        logging.error('A valid URL is required to make a request.')
    except requests.exceptions.TooManyRedirects:
        logging.error('Too many redirects.')
    except requests.exceptions.RequestException:
        #This is the exception that gets fired when requests doesn't know what went wrong
        logging.error('There was an ambiguous exception that occurred while handling your request.')
    except:
        # This should NEVER be fired.
        logging.error('An unexpected exception occurred while trying to send a REST request to the server.')
        logging.error(traceback.format_exc())
        raise
    return None


if __name__ == '__main__':
    '''
    Test code for http_rest module.
    '''
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE_PATH)
    baseurl = config['login']['baseurl']
    username = config['login']['username']
    password = config['login']['password']
    logging.config.fileConfig("config/log_config")
    logging.debug('Now testing http send module.')
    session = requests.Session()
    type_of_call = call_type.get
    params = {}
    apiurl = '/api/rest/auth/get'
    print('about to send request')
    rest_request(session, type_of_call, baseurl=baseurl, apiurl=apiurl, proxy=False)
        

