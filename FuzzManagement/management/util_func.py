from __future__ import unicode_literals
from django.conf import settings
import os


def handle_uploaded_file(directory, filename, data):
    full_path = os.path.join(settings.MEDIA_ROOT, directory)
    full_filename = os.path.join(full_path, filename)

    print "full_path : " + full_path
    print "full_filename : " + full_filename
    print "data : " + data 

    if not os.path.exists(full_path):
        os.mkdir(full_path)

    with open(full_filename, 'wb+') as f:
        f.write(data)


