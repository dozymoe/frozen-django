import os
# where `waf` will store its configuration
top = '.'
# directory for temporary files created during build process
out = '.BUILD'

# Constants

# stages, for example: 'dev' will provide separate build environment with
# commands like `waf build_dev` and `waf clean_dev`, that is build variants
if 'PROJECT_VARIANT' in os.environ:
    STAGES = (os.environ['PROJECT_VARIANT'],)
else:
    STAGES = ('dev', 'stage', 'prod')


def build(bld):
    # load main configuration file
    import pystache, yaml
    from pybuildtool.misc.resource import prepare_targets
    from pybuildtool.misc.yaml_utils import OrderedDictYAMLLoader
    conf_file = os.path.join(bld.path.abspath(), 'build.yml')
    with open(conf_file) as f:
        tasks = pystache.render(f.read(), dict(os.environ))
        conf = yaml.load(tasks, Loader=OrderedDictYAMLLoader)
    # parse data as waf tasks
    prepare_targets(conf, bld)


def options(opt):
    # add loadable modules from waf root directory
    import sys
    sys.path.append(opt.path.abspath())
    # load predefined tools from pybuildtool
    from imp import find_module
    pybuildtool_dir = find_module('pybuildtool')[1]
    addons_dir = os.path.join(pybuildtool_dir, 'addons')
    opt.load('watch', tooldir=addons_dir)


def configure(ctx):
    # load predefined tools from pybuildtool
    from imp import find_module
    pybuildtool_dir = find_module('pybuildtool')[1]
    tools_dir = os.path.join(pybuildtool_dir, 'tools')
    #ctx.load('ansibleplay', tooldir=tools_dir)
    #ctx.load('browserify', tooldir=tools_dir)
    #ctx.load('clean-css', tooldir=tools_dir)
    #ctx.load('concat', tooldir=tools_dir)
    #ctx.load('cp', tooldir=tools_dir)
    #ctx.load('cppcheck', tooldir=tools_dir)
    #ctx.load('dot', tooldir=tools_dir)
    #ctx.load('doxygen', tooldir=tools_dir)
    #ctx.load('gzip', tooldir=tools_dir)
    #ctx.load('handlebars', tooldir=tools_dir)
    #ctx.load('html-linter', tooldir=tools_dir)
    #ctx.load('jinja', tooldir=tools_dir)
    #ctx.load('jscs', tooldir=tools_dir)
    #ctx.load('jshint', tooldir=tools_dir)
    #ctx.load('less', tooldir=tools_dir)
    #ctx.load('lftp', tooldir=tools_dir)
    #ctx.load('metadata2fontface', tooldir=tools_dir)
    #ctx.load('msbuild', tooldir=tools_dir)
    #ctx.load('mustache', tooldir=tools_dir)
    #ctx.load('node-sass', tooldir=tools_dir)
    #ctx.load('nuget_restore', tooldir=tools_dir)
    #ctx.load('nunjucks', tooldir=tools_dir)
    #ctx.load('patch', tooldir=tools_dir)
    #ctx.load('pngcrush', tooldir=tools_dir)
    #ctx.load('postcss', tooldir=tools_dir)
    #ctx.load('protoc', tooldir=tools_dir)
    ctx.load('pylint', tooldir=tools_dir)
    #ctx.load('requirejs', tooldir=tools_dir)
    #ctx.load('restructuredtext-lint', tooldir=tools_dir)
    #ctx.load('runit_sv', tooldir=tools_dir)
    #ctx.load('roscpplint', tooldir=tools_dir)
    #ctx.load('scp', tooldir=tools_dir)
    ctx.load('shell', tooldir=tools_dir)
    #ctx.load('sphinx-apidoc', tooldir=tools_dir)
    #ctx.load('sphinx-build', tooldir=tools_dir)
    #ctx.load('splint', tooldir=tools_dir)
    #ctx.load('stylelint', tooldir=tools_dir)
    #ctx.load('stylus', tooldir=tools_dir)
    #ctx.load('ttf2eot', tooldir=tools_dir)
    #ctx.load('ttf2svg', tooldir=tools_dir)
    #ctx.load('ttf2woff', tooldir=tools_dir)
    #ctx.load('uglify-js', tooldir=tools_dir)
    #ctx.load('unzip', tooldir=tools_dir)
    #ctx.load('webpack', tooldir=tools_dir)
    #ctx.load('woff2svg', tooldir=tools_dir)
    #ctx.load('woff2ttf', tooldir=tools_dir)


from waflib.Build import BuildContext, CleanContext
from pybuildtool.core.context import WatchContext

for index, stage in enumerate(STAGES):
    for build_class in (BuildContext, CleanContext, WatchContext):
        if index == 0:
            build_class.variant = stage
            continue

        name = build_class.__name__.replace('Context', '').lower()
        class TempClass(build_class):
            cmd = name + '_' + stage
            variant = stage
