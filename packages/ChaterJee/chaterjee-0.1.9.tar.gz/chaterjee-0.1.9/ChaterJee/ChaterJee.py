import os, sys
import time
from datetime import datetime
import urllib.parse
import asyncio
import pickle
import html
import traceback
import logging, json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters, PollAnswerHandler, PollHandler
from telegram.constants import ParseMode
import os.path
import threading
from subprocess import PIPE, Popen
from pathlib import Path

start_txt = \
"""
I am ChaterJee, a Research assistant Bot developed by Pallab Dutta in 2025.

ChaterJee helps you to:
    - Receive research updates
    - Start new computational experiments

even when you are at a remote location.

"""

class ChatLogs:
    def __init__(self, TOKEN, CHATID):
        self.home = Path.home()
        self.TOKEN = TOKEN
        self.CHATID = CHATID
        self.txt = ''
        self.fig = ''
        self.path = os.popen('pwd').read()[:-1]
        self.smsID = []
        self.dict = {}
        self.jobs = {}

    def cmdTRIGGER(self, read_timeout=7, get_updates_read_timeout=42):
        application = ApplicationBuilder().token(self.TOKEN).read_timeout(read_timeout)\
                .get_updates_read_timeout(get_updates_read_timeout).build()

        start_handler = CommandHandler('start', self.start)
        application.add_handler(start_handler)

        fEdit_handler = CommandHandler('edit', self.EditorBabu)
        application.add_handler(fEdit_handler)

        cmd_handler = CommandHandler('sh', self.commands)
        application.add_handler(cmd_handler)

        #jobs_handler = CommandHandler('jobs', self.ShowJobs)
        #application.add_handler(jobs_handler)

        jobs_handler = ConversationHandler(\
        entry_points=[CommandHandler("jobs", self.ShowJobs)],\
        states={
            0: [MessageHandler(filters.Regex(f"^({'|'.join(list(self.jobs.keys()))})$"), self.StatJobs)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        application.add_handler(jobs_handler)
        #add_handler = CommandHandler('add', addDICT)
        #application.add_handler(add_handler)
        #run_handler = CommandHandler('run', runCMD)
        #application.add_handler(run_handler)
        #com_handler = CommandHandler('com', comCMD)
        #application.add_handler(com_handler)
        #exit_handler = CommandHandler('exit', exitCMD)
        #application.add_handler(exit_handle)
        #clear_handler = CommandHandler('clear', clsCMD)
        #application.add_handler(clear_handler)
        #jedit_handler = CommandHandler('edit', editJSON)        # JSON file editor
        #application.add_handler(jedit_handler)

        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        #application.add_handler(MessageHandler(filters.TEXT, self.commands))

        application.run_polling() 

    def strSMS(self, update, context):
        self.smsID.append(update.message.message_id)
        self.txt=update.message.text
        cmd = self.txt.split(' ')[0]
        args = self.txt.split(' ')[1:]
        if cmd == '/add':
            self.addDICT(args)
        elif cmd == '/run':
            self.cmdRUN(args)
        elif cmd == '/com':
            self.cmdCOM(args)
        elif cmd == '/exit':
            self.EXIT()
        elif cmd == '/clear':
            self.cls()
        elif cmd[0] == '/':
            self.txt = 'command not found !'
            self.sendUPDATE()
        else:
            self.txt = "Sorry I can only read '/commands', not 'texts'."
            self.sendUPDATE()

    def addDICT(self, context):
        try:
            key = context[0]
            eql = context[1]
            if ('$' in key) and (eql == '='):
                val = context[2]
                self.dict[key]=val
                self.txt = 'added to dictionary'
            elif ('$' in key) and (eql == '-1'):
                del self.dict[key]
                self.txt = 'removed from dictionary'
            else:
                self.txt = 'pass the command as:\n/add $key = val'
        except:
            self.txt = 'pass the command as:\n/add $key = val'
        self.sendUPDATE()

    def fmtDICT(self, context):
        key = []
        idx = []
        c = context
        for i in range(len(context)):
            w = context[i]
            if '$' in w:
                key.append(w)
                idx.append(i)
        for j in range(len(idx)):
            val = self.dict[key[j]]
            c[idx[j]] = val
        return c

    #async def cmdRUN(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    def cmdRUN(self, context):
        context = self.fmtDICT(context)
        cmd0 = context[0]
        if cmd0=='cd':
            cmd1 = context[1]
            try:
                os.chdir(cmd1)
                self.txt=os.popen('pwd').read()
            except:
                self.txt='path not found'
        else:
            cmd=' '.join(context)
            try:
                self.txt=os.popen('%s'%(cmd)).read()
            except:
                self.txt='error !'
        self.sendUPDATE()

    def readout(self):
        time.sleep(1)
        fout=open('stdout.txt','r')
        ferr=open('stderr.txt','r')
        lout = fout.readlines()
        out = ' '.join(lout)
        lerr = ferr.readlines()
        err = ' '.join(lerr)
        #out = out.strip()
        #err = err.strip()
        if out == '' and err == '':
            self.txt = 'command executed !'
        elif out != '' and err == '':
            self.txt = 'out:\n%s\n'%(out)
        elif out == '' and err != '':
            self.txt = 'err:\n%s\n'%(err)
        else:
            self.txt = 'out:\n%s\nerr:\n%s\n'%(out,err)
        print(self.txt)
        fout.close()
        ferr.close()
        tout=open('stdout.txt','w')
        tout.close()
        terr=open('stderr.txt','w')
        terr.close()

    def cmdCOM(self, context):
        context = self.fmtDICT(context)
        if context[0]!='i' and context[0]!='kill':
            self.fout = open('stdout.txt','w')
            self.ferr = open('stderr.txt','w')
            self.p=Popen(context,stdin=PIPE,stdout=self.fout,stderr=self.ferr,universal_newlines=True,bufsize=0)
            self.fout.close()
            self.ferr.close()
        elif context[0]=='kill':
            self.txt = 'process terminated'
            self.p.terminate()
        else:
            comsg = ' '.join(context[1:])
            self.p.stdin.write(comsg+'\n')
        self.readout()
        
        #out,err = self.p.communicate()
        #out = ' '.join(self.p.stdout)
        #err = ' '.join(self.p.stderr)
        #self.txt = "out: \n%s\n\nerr: \n%s"%(out,err)
        self.sendUPDATE()

    def EXIT(self):
        os.chdir(self.path)
        self.txt = "Thanks! I am signing off."
        self.sendUPDATE()
        time.sleep(2)
        self.cls()
        threading.Thread(target=self.shutdown).start()

    def shutdown(self):
        self.updater.stop()
        self.updater.is_idle = False

    def cls(self):
        for i in self.smsID:
            self.BOT.delete_message(chat_id=self.CHATID, message_id=i)
        self.smsID = []

    def sendUPDATE(self):
        self.BOT.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = self.BOT.sendMessage(chat_id=self.CHATID, text=self.txt)
        self.smsID.append(msg.message_id)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        msg = await context.bot.send_message(chat_id=self.CHATID, text=start_txt)
        self.smsID.append(msg.message_id)

    def register_to_log(self, job_name: str, log_path: str):
        self.jobs[job_name] = log_path

    async def ShowJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        self.jobs = jobs

        reply_keyboard = [[f'{job}'] for job in list(self.jobs.keys())]
        msg = await update.message.reply_text("Select a job to get updates on",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select the job."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 0

    async def StatJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print("I'm inside StatJobs")
        job_name = update.message.text
        
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        self.jobs = jobs

        logDIR = Path(jobs[job_name]['logDIR'])
        logFILE = jobs[job_name]['logFILE']
        logIMAGE = jobs[job_name]['logIMAGE']
        
        txt = self.get_last_line(logDIR / logFILE)
        print(txt)

        if txt is not None:
            msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
            self.smsID.append(msg.message_id)

        try:
            with open(logDIR / logIMAGE, 'rb') as ffrb:
                msg = await context.bot.send_photo(chat_id=self.CHATID, photo=ffrb)
                self.smsID.append(msg.message_id)
        except:
            pass

        return ConversationHandler.END

    def get_last_line(self, filepath):
        with open(filepath, 'rb') as f:
            # Go to the end of file
            f.seek(0, 2)
            end = f.tell()

            # Step backwards looking for newline
            pos = end - 1
            while pos >= 0:
                f.seek(pos)
                char = f.read(1)
                if char == b'\n' and pos != end - 1:
                    break
                pos -= 1

            # Read from found position to end
            f.seek(pos + 1)
            last_line = f.read().decode('utf-8')
            return last_line.strip()

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass

    async def EditorBabu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print('Opening Json file in edit mode')
        if len(context.args) == 1:
            file_path = context.args[0]
            if os.path.exists(file_path):
                with open(file_path,'r') as ffr:
                    JsonStr = json.load(ffr)
                encoded_params = urllib.parse.quote(json.dumps(JsonStr))
                file_name = file_path.split('/')[-1]
                extender = f"?variables={encoded_params}&fileNAME={file_name}"
                msg = await update.message.reply_text(
                    "Editor-Babu is opening the Json file.",
                    reply_markup=ReplyKeyboardMarkup.from_button(
                        KeyboardButton(
                            text="Editor Babu",
                            web_app=WebAppInfo(url="https://pallab-dutta.github.io/EditorBabu"+extender),
                        )
                    ),
                )
            else:
                txt = f"File {file_path} not Found!"
                msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        else:
            txt = "Expected a JSON file as argument. Nothing provided."
            msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        
        self.smsID.append(msg.message_id)

    async def web_app_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None :
        data = json.loads(update.effective_message.web_app_data.data)
        formname = data['formNAME']
        if formname == 'EditorBabu':
            fileNAME = data['fileNAME']
            del data['formNAME']
            del data['fileNAME']
            if len(data):
                with open(fileNAME, 'r') as ffr:
                    JSdata = json.load(ffr)
                JSdata = {**JSdata, **data}
                with open(fileNAME, 'w') as ffw:
                    json.dump(JSdata, ffw, indent=4)
                txt = f"edits are saved to {fileNAME}"
            else:
                txt = f"No new changes! file kept unchanged."

        msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        self.smsID.append(msg.message_id)

    async def commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        cmd2run = ' '.join(context.args) #update.message.text.strip()
        cmd0 = cmd2run.split(' ')[0]
        if cmd0=='cd':
            cmd1 = cmd2run[3:]
            try:
                os.chdir(cmd1)
                txt=os.popen('pwd').read()
            except:
                txt='path not found'
        elif cmd0=='clear':
            for i in self.smsID:
                await context.bot.delete_message(chat_id=self.CHATID, message_id=i)
                self.smsID = []
            txt=''
        else:
            print('command: ',cmd2run)
            cmd=cmd2run
            try:
                txt=os.popen('%s'%(cmd)).read()
            except:
                txt='error !'
        if len(txt):
            msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
            self.smsID.append(msg.message_id)


class NoteLogs:
    def __init__(self):
        self.home = Path.home()
        self.jobNAME = None
        self.logDIR = None
        self.logFILE = None
        self.logIMAGE = None

    def write(self, jobNAME: str, logDIR: str = None, logSTRING: str = None, logFILE: str = 'log_file.out', logIMAGE: str = 'log_file.png'):
        if logDIR is None:
            pwd = Path.cwd()
            _logDIR = pwd / jobNAME
            _logDIR.mkdir(exist_ok=True)
        else:
            _logDIR = Path(logDIR)

        with open(_logDIR / logFILE, 'a') as ffa:
            print(f"\n{logSTRING}",file=ffa)

        _logFILE = _logDIR / logFILE
        _logIMAGE = _logDIR / logIMAGE

        logDIR = str(_logDIR)

        self.jobNAME = jobNAME
        self.logDIR = logDIR
        self.logFILE = logFILE
        self.logIMAGE = logIMAGE
        self.save_job_JSON()

    def save_job_JSON(self):
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        jobs[self.jobNAME] = {\
                "logDIR": self.logDIR, \
                "logFILE": self.logFILE, \
                "logIMAGE": self.logIMAGE \
                }
        with open(jobs_file, 'w') as ffw:
            json.dump(jobs, ffw, indent=4)


