FROZEN DJANGO
-------------

Export webpages created by your Django views into html files.

It is dumb, it won't deploy the files to AWS for instance, and won't collect
assets from static files or uploaded files.

The assumption is that the build process will be triggered by Django signals,
for example when a BlogPost was created, and will only rebuild the related
html (or json) files.


Requirements
============

 * add `frozen_django` to your INSTALLED_APPS
 * will only process named urls
 * will only process urls with file extensions (.html, .json, .js, .xml, etc.)
 * Django Views with pagination must have `<link rel="next">` in their content


Settings
========

 * FROZEN_URL (optional, must be absolute url, `https://example.com/`)
 * FROZEN_ROOT (optional)
 * FROZEN_MIDDLEWARE (optional)


API
===

 * Django Command `freeze_view`
 * uwsgi task `freeze_view`
