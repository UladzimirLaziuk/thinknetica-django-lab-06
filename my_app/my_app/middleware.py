import logging
import time
import re

from django.utils.deprecation import MiddlewareMixin

MOBILE_AGENT_RE = re.compile(r".*(iphone|mobile|androidtouch)", re.IGNORECASE)


def metric_middleware(get_response):
    def middleware(request):
        # Get beginning stats
        start_time = time.perf_counter()

        # Process the request
        response = get_response(request)

        # Get ending stats
        end_time = time.perf_counter()

        # Calculate stats
        total_time = end_time - start_time

        # Log the results
        logger = logging.getLogger('debug')
        logger.info(f'Total time: {(total_time):.2f}s')
        print(f'Total time: {(total_time):.2f}s')

        return response

    return middleware


class MobileDetectionMiddleware(MiddlewareMixin):
    """
    Useful middleware to detect if the user is
    on a mobile device.
    """

    def process_request(self, request):
        is_mobile = False

        if request.META.get('HTTP_USER_AGENT'):
            user_agent = request.META['HTTP_USER_AGENT']

            # Test common mobile values.
            pattern = "(up.browser|up.link|mmp|symbian|smartphone|midp|wap|phone|windows ce|" \
                      "pda|mobile|mini|palm|netfront)"
            prog = re.compile(pattern, re.IGNORECASE)
            match = prog.search(user_agent)

            if match:
                is_mobile = True
            else:
                # Nokia like test for WAP browsers.
                # http://www.developershome.com/wap/xhtmlmp/xhtml_mp_tutorial.asp?page=mimeTypesFileExtension

                if hasattr(request.META, 'HTTP_ACCEPT'):
                    http_accept = request.META['HTTP_ACCEPT']

                    pattern = r"application/vnd\.wap\.xhtml\+xml"
                    prog = re.compile(pattern, re.IGNORECASE)

                    match = prog.search(http_accept)

                    if match:
                        is_mobile = True

            if not is_mobile:
                # Now we test the user_agent from a big list.
                user_agents_test = ("w3c ", "acs-", "alav", "alca", "amoi", "audi",
                                    "avan", "benq", "bird", "blac", "blaz", "brew",
                                    "cell", "cldc", "cmd-", "dang", "doco", "eric",
                                    "hipt", "inno", "ipaq", "java", "jigs", "kddi",
                                    "keji", "leno", "lg-c", "lg-d", "lg-g", "lge-",
                                    "maui", "maxo", "midp", "mits", "mmef", "mobi",
                                    "mot-", "moto", "mwbp", "nec-", "newt", "noki",
                                    "xda", "palm", "pana", "pant", "phil", "play",
                                    "port", "prox", "qwap", "sage", "sams", "sany",
                                    "sch-", "sec-", "send", "seri", "sgh-", "shar",
                                    "sie-", "siem", "smal", "smar", "sony", "sph-",
                                    "symb", "t-mo", "teli", "tim-", "tosh", "tsm-",
                                    "upg1", "upsi", "vk-v", "voda", "wap-", "wapa",
                                    "wapi", "wapp", "wapr", "webc", "winw", "winw",
                                    "xda-",)

                test = user_agent[0:4].lower()
                if test in user_agents_test:
                    is_mobile = True

        request.is_mobile = is_mobile
