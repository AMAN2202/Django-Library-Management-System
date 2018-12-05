from django.shortcuts import render


class GoogleSearch(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):


        # to search
        query = u'{}: {}'.format(exception.__class__.__name__, str(exception))

        #j=list(search(query, tld="co.in", num=1, stop=1, pause=2))
        j=query
        print(j)
        import webbrowser

        webbrowser.open_new("https://www.google.co.in/search?q="+j)
        return None