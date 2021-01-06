from flask import Flask, request, render_template, flash, session, send_file
import os, subprocess, zipfile
import secrets
from datetime import datetime
import maxminddb
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.secret_key = secrets.token_urlsafe(16)
app.config['UPLOAD_FOLDER'] = "uploads"
ALLOWED_EXTENSIONS = ['fasta', 'fa']



def is_allowed_file(filename):
    return filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def launch_app(filepaths, token, submit_mode='slurm', email='', mailserver='internal'):
    '''
    Launch SISTR command-line application directly on system with or without job scheduler
    :param filename:
    :param token:
    :return:
    '''

    body = 'Dear user,\nPlease download your results from {} using token {}\n\nSincerely,\nSISTR TEAM'.format("XXXX",
                                                                                                              token)
    replace_fields_dictionary = {'{{input_filepaths}}': filepaths,
                                 '{{token}}': token,
                                }
    if mailserver=="external":
        replace_fields_dictionary['{{send_email}}'] = 'send_gmail_notification.py -e ' + email + ' -t ' + token
    elif mailserver == "internal":
        replace_fields_dictionary['{{send_email}}'] = "echo \""+body+"\" | " \
                                                      "mail -v -s \"SISTR: Your job {} is ready\" {}".format(token,email)
    else:
        raise ("No email client specified or unexpected value. {}".format(mailserver))

    tmp_workdir = 'tmp/{}'.format(token)
    launch_script_path = "tmp/{}/launch_script_{}.sh".format(token,token)


    if not os.path.exists(tmp_workdir):
        os.makedirs(tmp_workdir)

    #read launch script templare and modify it


    if submit_mode == "slurm":
        template_script = open(file="static/bash_templates/slurm_header.sh", mode="r").read()
        cmd = "sbatch {}".format(launch_script_path)
    elif submit_mode == "direct":
        template_script = open(file="static/bash_templates/launch_template.sh", mode="r").read()
        cmd = "bash {}".format(launch_script_path)
    else:
        raise Exception("Invalid submission mode. Supported modes: direct or slurm")

    #generate launch script
    #template_script = template_script.replace('{{input_filepaths}}'," ".join(replace_fields_dictionary['{input_filepaths}']))


    for key, value in replace_fields_dictionary.items():
        if isinstance(value, list):
            template_script = template_script.replace(key," ".join(value))
        else:
            template_script = template_script.replace(key, value)


    open(file=launch_script_path,mode="w").write(template_script)


    logfile = open("tmp/frontend-log.log", 'a')
    subprocess.Popen(cmd, stdout=logfile, stderr=logfile, shell=True)


    #if process.returncode == 0:
    #    shutil.move("tmp/{}".format(result_file_name), "results/{}".format(result_file_name))
    #else:
    #    app.logger.error("Sample {} failed".format(filename))
    #return process.returncode

    #subprocess.run("source activate sistr && sistr -h".split(" "), check=True)
def is_results_exist(token):
    result_dirs = os.listdir("results/")
    if token in result_dirs:
        return True
    else:
        return  False


def zip_results(token):
    folder_result_path = 'results/' + token
    filenames = [filename for filename in os.listdir(folder_result_path)]
    zipfilepath = 'tmp/results-{}.zip'.format(token)
    app.logger.info("Zipped the following files: {}".format(filenames))

    zipf = zipfile.ZipFile(zipfilepath, 'w')

    for file in filenames:
        zipf.write(os.path.join(folder_result_path, file))
    zipf.close()
    return zipfilepath

def record_submission_stats(nfiles, token, client_ip):

    try:
        reader = maxminddb.open_database('static/GeoLite2-City-MaxMind.mmdb')
        json_ip = reader.get(client_ip)
        reader.close()
    except:
        json_ip = None


    if json_ip:
        client_country = json_ip["country"]["names"]["en"]
        client_town = json_ip["city"]["names"]["en"]
    else:
        client_ip = "NA"; client_country = "NA"; client_town = "NA"

    now=datetime.now()




    if not os.path.exists("stats/submissions_stats.txt"):
        with open(file="stats/submissions_stats.txt", mode="w") as fp:
            fp.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format("IP", "Country", "City", "Token", "#Genomes", "Date", "Time(EST)"))


    with open(file="stats/submissions_stats.txt", mode="a") as fp:
            fp.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(client_ip, client_country, client_town,token, nfiles,
                                                   now.strftime("%d/%m/%Y"), now.strftime("%H:%M:%S")
                                                   ))




@app.route('/', methods=["GET","POST"])
def upload():
    print(request.form.get("submit2sistr"), len(request.files),request.files)
    print(request.form)
    #print(request.method)
    if 'session_upload_dir' not in session:
        session['session_upload_dir'] = secrets.token_hex(4)

    print(session['session_upload_dir'])
    if request.method == 'GET':
        session.clear()
        session['uploaded_files']=[]
    elif request.method == 'POST' and 'uploaded_files' not in session:
        session['uploaded_files'] = []

    if request.method == 'POST':
        filesuploaded_list = session['uploaded_files']

        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'],session['session_upload_dir']), exist_ok=True) #make directory
        for key in request.files:
            file=request.files[key]

            if is_allowed_file(file.filename):

                input_file_path = os.path.join(app.config['UPLOAD_FOLDER'], session['session_upload_dir'], file.filename)
                file.save(input_file_path)
                app.logger.info("Finished uploading {}".format(file.filename))

                filesuploaded_list.append(input_file_path)

        session['uploaded_files'] = filesuploaded_list


        if  request.form.get("submit_genomes") == "Submit":
           print(request.form)
           if session["uploaded_files"] != []:
               submit_token = secrets.token_hex(4)
               client_ip = request.form['ip']
               email=request.form["email"]

               launch_app(session['uploaded_files'], submit_token, "slurm", email)
               app.logger.info("Launched samples {}".format(session['uploaded_files']))

               flash('Submitted {} file(s) to SISTR with submission token {}'.format(
                   len(session['uploaded_files']),
                   submit_token), 'info')
               flash(session['uploaded_files'],'info')

               record_submission_stats(len(session["uploaded_files"]), submit_token, client_ip)
               session['uploaded_files'] = []
           else:
               flash("No files to submit","error")


    return render_template('index.html')

@app.route('/results', methods=["GET","POST"])
def get_results():
    print(request.method, request.form)
    if request.method == "POST":
        if 'reset_btn' in request.form:
            render_template('results.html')
        elif request.form['token']:
            token = request.form['token']
            if is_results_exist(token):
                zipfilepath = zip_results(token)


                return send_file(zipfilepath,
                                 mimetype='text/html',
                                 attachment_filename='results_{}.zip'.format(token),
                                 as_attachment=True)
            else:
                flash("Result not yet found. Try out later or check queue status", 'error')

        else:
            flash("No token provided", 'error')

    return render_template('results.html')


@app.route('/queue', methods=["GET"])
def update_queue():
    stdout, stderr = subprocess.Popen(['squeue --format "%.8j %.8T %.4M %V"'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              shell=True).communicate()

    if stderr:
        flash(stderr.decode("utf-8"), 'error')
    return render_template('queue.html', slurm_output=stdout.decode("utf-8"))


@app.route('/history', methods=["GET"])
def get_history():
    max_lines = 50
    if os.path.exists("stats/submissions_stats.txt"):
        with open(file="stats/submissions_stats.txt", mode="r") as fp:
            history_list=fp.readlines()
            if len(history_list) < max_lines:
                max_lines = len(history_list)-1
            history_str = "".join([history_list[0]]+history_list[-max_lines:])
        return render_template('history.html', history_str=history_str)
    else:
        flash("No history file is available. Run some jobs", 'error')
        return render_template('history.html')



if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0', port=5010)


#docker build . sistr-server-dev:latest
#docker run -it -p 5000:5000 --rm  -v ~/WORK/SISTR/SISTR-website-dev/SISTR-website-repo:/mnt sistr-server-dev:latest  bash
#export FLASK_APP=app.py
#flask run