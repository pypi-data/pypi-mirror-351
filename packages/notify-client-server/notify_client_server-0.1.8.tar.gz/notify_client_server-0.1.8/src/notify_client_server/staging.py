import os

from .cfg import cfg


# -------------------
## generate any files necessary for use in the service, client, etc.
class Staging:
    # -------------------
    ## generate the service file based on the template
    #
    # @return None
    def gen_service_file(self):
        dst = os.path.join('webhost', cfg.svc_name)
        if os.path.isfile(dst):
            os.remove(dst)

        src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template_notify_server.service')
        with open(src, 'r', encoding='utf-8') as src_fp:
            with open(dst, 'w', encoding='utf-8') as dst_fp:
                while True:
                    line = src_fp.readline()
                    if line == '':
                        break

                    line = cfg.translate_service_only(line)
                    dst_fp.write(line)
