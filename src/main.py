import os, time, shutil, logging, subprocess
import tornado.ioloop
import tornado.web

port = 8000
buf_size = 4*1024
main_url= r"/2pdf"
tmp_main_folder = "/tmp/"
out_main_folder = "/opt/"
log_file_name = '/var/log/2pdf.log'


logger = logging.getLogger('word2pdf')
logger.setLevel(logging.DEBUG)
logger.propagate = False
# create file handler which logs even debug messages
fh = logging.FileHandler(log_file_name)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

class MainHandler(tornado.web.RequestHandler):
    def word2pdf(self, file, out_dir):
        p = subprocess.Popen(['soffice','--headless','--convert-to','pdf','--outdir',out_dir,file], cwd="/usr/bin/")
        p.wait()

    # handle a post request
    def post(self):
        logger.info("UploadFiles")
        files = []
        files_tmp = []
        tmp_folder = tmp_main_folder + str(time.time()).replace(".", "") + "/"
        os.mkdir(tmp_folder)
        out_folder = out_main_folder + str(time.time()).replace(".", "") + "/"
        os.mkdir(out_folder)
        try:
            files = self.request.files['files']
            files.sort()
        except:
            pass
        #TODO вывод ошибки in response
        for xfile in files:
            file = xfile['filename']
            fullname = tmp_folder + file
            files_tmp.append(fullname)
            with open(fullname, "wb") as out:
                out.write(xfile['body'])
                logger.info("Upload file = " + file)
        if len(files_tmp):
            for file in files_tmp:
                ext = os.path.splitext(file)[1].lower()
                if ext =='.docx':
                    self.word2pdf(file, out_folder)
                    logger.info("Convert Word file = " + file + " ---> to Folder " + out_folder)
                if ext =='.pdf':
                    shutil.copy(file, out_folder)
                    logger.info("Copy PDF file = " + file + " ---> to Folder " + out_folder)
            # TODO проверка, что есть файлы для склейки
            outfile = "out_" + str(time.time()).replace(".", "") + ".pdf"
            os.system("cd " + out_folder + " && /usr/bin/pdftk *.pdf cat output " + outfile)
            logger.info("Create out file = " + out_folder + outfile)
            f_name = 'out.pdf'
            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + f_name)
            with open(out_folder + outfile, 'rb') as f:
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    self.write(data)
            self.finish()
        else:
            pass
            # TODO вывод ошибки response файлы не найдены
        shutil.rmtree(tmp_folder, ignore_errors=True)
        shutil.rmtree(out_folder, ignore_errors=True)

def make_app():
    logger.info('Rest API started.')
    return tornado.web.Application([
        (main_url, MainHandler)
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(port)
    tornado.ioloop.IOLoop.current().start()
