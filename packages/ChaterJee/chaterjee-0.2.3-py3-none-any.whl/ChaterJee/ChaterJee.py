import os, sys
import time
from datetime import datetime
import urllib.parse
import asyncio
import pickle
import html
import traceback
import logging, json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Updater, ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters, PollAnswerHandler, PollHandler
from telegram.constants import ParseMode
import os.path
import threading
from subprocess import PIPE, Popen
from pathlib import Path

start_txt = \
"""
I am ChaterJee, a Research assistant Bot developed by Pallab Dutta in 2025.

*TEXT*
acts as a bash command and runs on host terminal.

*COMMANDS*
/start : returns this text.
/jobs : shows your jobs
/clear : clears chat history
/edit file.json : let you edit the file.json

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
        #que = asyncio.Queue()
        application = ApplicationBuilder().token(self.TOKEN).read_timeout(read_timeout)\
                .get_updates_read_timeout(get_updates_read_timeout).build()
        #updater = Updater(application.bot, update_queue=que)

        start_handler = CommandHandler('start', self.start)
        application.add_handler(start_handler)

        fEdit_handler = CommandHandler('edit', self.EditorBabu)
        application.add_handler(fEdit_handler)

        #cmd_handler = CommandHandler('sh', self.commands)
        #application.add_handler(cmd_handler)

        cancel_handler = CommandHandler('cancel', self.cancel)
        application.add_handler(cancel_handler)

        jobs_handler = ConversationHandler(\
        entry_points=[CommandHandler("jobs", self.ShowJobs), CommandHandler("clear", self.ask2clear)],\
        states={
            0: [MessageHandler(filters.Regex("^(JOB)"), self.StatJobs)],
            1: [MessageHandler(filters.Regex("^(Yes|No)$"), self.ClearChat)],
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )
        application.add_handler(jobs_handler)

        application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, self.web_app_data))
        application.add_handler(MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^(JOB:|Yes$|No$)")), self.commands))

        #await application.shutdown()
        #await application.initialize()

        #updater = Updater(application.bot, update_queue=que)
        #await updater.initialize()
        #await updater.start_polling()
        application.run_polling()

    async def sendUpdate(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if len(self.txt):
            await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
            msg = await context.bot.send_message(chat_id=self.CHATID, text=self.txt, parse_mode='Markdown')
            self.smsID.append(msg.message_id)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        self.txt = start_txt
        await self.sendUpdate(update, context)

    def register_to_log(self, job_name: str, log_path: str):
        self.jobs[job_name] = log_path

    async def ShowJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        self.jobs = jobs

        reply_keyboard = [[f'{job}'] for job in list(self.jobs.keys())]
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text("Select a job to get updates on",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select the job."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 0

    async def StatJobs(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        job_name = update.message.text
        
        jobs_file = self.home / ".data" / "JOB_status.json"
        with open(jobs_file, 'r') as ffr:
            jobs = json.load(ffr)
        self.jobs = jobs

        logDIR = Path(jobs[job_name]['logDIR'])
        logFILE = jobs[job_name]['logFILE']
        logIMAGE = jobs[job_name]['logIMAGE']
        
        self.txt = self.get_last_line(logDIR / logFILE)

        if self.txt is None:
            self.txt = 'No updates found'
            #await self.sendUpdate(update, context)
            #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
            #self.smsID.append(msg.message_id)
        
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
            self.txt, reply_markup=ReplyKeyboardRemove()
        )
        self.smsID.append(msg.message_id)

        try:
            with open(logDIR / logIMAGE, 'rb') as ffrb:
                await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
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
        self.smsID.append(update.message.message_id)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
        "Keyboard is refreshed!", reply_markup=ReplyKeyboardRemove()
        )
        self.smsID.append(msg.message_id)
        return ConversationHandler.END

    async def EditorBabu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        if len(context.args) == 1:
            file_path = context.args[0]
            if os.path.exists(file_path):
                with open(file_path,'r') as ffr:
                    JsonStr = json.load(ffr)
                encoded_params = urllib.parse.quote(json.dumps(JsonStr))
                file_name = file_path.split('/')[-1]
                extender = f"?variables={encoded_params}&fileNAME={file_name}"
                await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
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
                self.txt = f"File {file_path} not Found!"
                #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        else:
            self.txt = "Expected a JSON file as argument. Nothing provided."
            #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        
        #self.smsID.append(msg.message_id)
        await self.sendUpdate(update, context)

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
                self.txt = f"edits are saved to {fileNAME}"
            else:
                self.txt = f"No new changes! file kept unchanged."

        #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        #self.smsID.append(msg.message_id)
        await self.sendUpdate(update, context)

    async def commands(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        #cmd2run = ' '.join(context.args) #update.message.text.strip()
        cmd2run = update.message.text.strip()
        cmd0 = cmd2run.split(' ')[0]
        if cmd0[0]=='/':
            print('It came here')
            pass
        elif cmd0=='cd':
            cmd1 = cmd2run[3:]
            try:
                os.chdir(cmd1)
                self.txt=os.popen('pwd').read()
            except:
                self.txt='path not found'
        elif cmd0=='clear':
            self.txt="This clears the terminal screen!\nTo clear telegram screen type /clear"
        elif cmd0=='pkill':
            self.txt="pkill cannot be called."
        else:
            print('command: ',cmd2run)
            cmd=cmd2run
            try:
                self.txt=os.popen('%s'%(cmd)).read()
            except:
                self.txt='error !'
        await self.sendUpdate(update, context)
        #msg = await context.bot.send_message(chat_id=self.CHATID, text=txt)
        #self.smsID.append(msg.message_id)

    async def ClearChat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.smsID.append(update.message.message_id)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text(
        "Full chat history will be cleared", reply_markup=ReplyKeyboardRemove()
        )
        self.smsID.append(msg.message_id)
        for i in self.smsID:
            await context.bot.delete_message(chat_id=self.CHATID, message_id=i)
        
        self.smsID = []
        return ConversationHandler.END

    async def ask2clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        self.smsID.append(update.message.message_id)
        reply_keyboard = [['Yes','No']]
        print(reply_keyboard)
        await context.bot.sendChatAction(chat_id=self.CHATID, action="typing")
        msg = await update.message.reply_text("Entire chat history in the current session will be cleared. Proceed?",\
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Select to proceed."\
        ),\
        )
        self.smsID.append(msg.message_id)
        return 1


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

        self.jobNAME = f"JOB: {jobNAME}"
        self.logDIR = logDIR
        self.logFILE = logFILE
        self.logIMAGE = logIMAGE
        self.save_job_JSON()

    def save_job_JSON(self):
        _data = self.home / ".data"
        _data.mkdir(exist_ok=True)
        jobs_file = _data / "JOB_status.json"
        try:
            with open(jobs_file, 'r') as ffr:
                jobs = json.load(ffr)
        except FileNotFoundError:
            jobs = {}
        jobs[self.jobNAME] = {\
                "logDIR": self.logDIR, \
                "logFILE": self.logFILE, \
                "logIMAGE": self.logIMAGE \
                }
        with open(jobs_file, 'w') as ffw:
            json.dump(jobs, ffw, indent=4)


