import datetime
import os
import shutil
import time

from falcon_logger import FalconLogger
from notify_client_server.client import NotifyClient
from notify_client_server.os_specific import OsSpecific
from notify_client_server.svc import svc


# ---------------------
## Base class for Backups using rsync
class BackupBase:
    # ---------------------
    ## constructor
    def __init__(self):
        svc.log = FalconLogger()
        svc.log.set_max_entries(1)

        ## tag for backups
        self.tag = ''

        ## overall return code
        self.overallrc = 0
        ## number of backups done
        self.backups_done = 0
        ## number of warnings issued
        self.backups_warn = 0
        ## number of errors issued
        self.backups_failed = 0

        ## the backup host; usually an ssh compatible hostname or identifier in .ssh/config
        self.bkp_host = 'unset'
        ## the root directory in the backup server to copy to
        self.bkp_root = 'unset'
        ## a callback function for printing to stdout
        self.print_cb = None

        ## list of rsync opts
        self.opts = ''

        ## reference to NotifyClient
        self.client = None

        ## directory that holds incremental differences per backup
        self._incdir = 'unset'

        # for final notification
        ## used to calculate total time for the backup
        self._start_time = time.time()
        ## additional description text for the final notification
        self._notify_desc_extra = ''

    # ---------------------
    ## the current hostname being backed up
    #
    # @return hostname
    @property
    def this(self):
        return OsSpecific.hostname

    # ---------------------
    ## get reference to svc logger
    #
    # @return logger
    @property
    def log(self):
        return svc.log

    # ---------------------
    ## initialize
    #
    # @return None
    def init_base(self):
        self.client = NotifyClient(svc.log)

        self.overallrc = 0
        self.backups_done = 0
        self.backups_warn = 0
        self.backups_failed = 0

        self._setup_incdir()

    # ---------------------
    ## report of basic information for this backup
    #
    # @return None
    def report_base(self):
        svc.log.line(f'{self.tag}: {"this pc": <10} {self.this}')
        svc.log.line(f'{self.tag}: {"bkp host": <10} {self.bkp_host}')
        svc.log.line(f'{self.tag}: {"bkp root": <10} {self.bkp_root}')
        svc.log.line(f'{self.tag}: {"inc dir": <10} {self._incdir}')

    # ---------------------
    ## perform a backup of a directory formed by root + bkp_dir
    #
    # @param root        the root of the directory to back up
    # @param bkp_dir     the remainder of the directory to back up
    # @param extra_opts  additional rsync options to use for this directory
    # @return None
    def do_backup(self, root, bkp_dir, extra_opts=''):
        self.backups_done += 1
        if root == '/':
            src = f'/{bkp_dir}/'
        else:
            root = os.path.expanduser(root)
            src = f'{root}/{bkp_dir}/'

        opts_str = extra_opts[:60]
        svc.log.highlight(f'{self.tag}: dobackup starting: {src} extra_opts={opts_str}...')

        if not os.path.isdir(src):
            desc = f'does not exist   : {src}'
            svc.log.warn(f'{self.tag}: {desc}')
            self.backups_warn += 1
            self.notify('warn', desc)
            return

        if self.bkp_host is None:
            os.makedirs(self.bkp_root, exist_ok=True)
            dst = f'{self.bkp_root}/{bkp_dir}/'
        else:
            dst = f'{self.bkp_host}:{self.bkp_root}/{bkp_dir}/'
        # svc.log.dbg(f'src={src} dst={dst}')

        cmd = f'rsync {self.opts} {extra_opts} --backup-dir="{self._incdir}" "{src}" "{dst}"'
        # svc.log.dbg(f'cmd={cmd}')

        rc, lines = OsSpecific.run_cmd(cmd, print_cb=self.print_cb)
        self._check_rc(rc, f'do_backup path:{src}')
        desc = f'rc:{rc} backup:{src}'
        if rc != 0:
            # TODO determine error and update desc"
            svc.log.num_output(lines)

            self.backups_failed += 1
            self.notify('err', desc)
        self.overallrc += rc

    # ---------------------
    ## check the return code and print an appropriate line to stdout.
    # update the overall rc as appropriate
    #
    # @param rc     the return code
    # @param msg    the message to print
    # @return None
    def _check_rc(self, rc, msg):
        svc.log.check(rc == 0, msg)
        self.overallrc += rc

    # --------------------
    ## create an incremental backup directory to hold differences detected by rsync
    #
    # @return None
    def _setup_incdir(self):
        dts = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        if self.bkp_host is not None:
            self._incdir = f'{self.bkp_root}/inc_backup_{dts}'
        elif self.bkp_root.startswith('/'):
            self._incdir = f'{self.bkp_root}/inc_backup_{dts}'
        else:
            self._incdir = f'./{self.bkp_root}/inc_backup_{dts}'

    # ---------------------
    ## send notification with the overall status of the backup.
    #  * total time
    #  * overall rc
    #  * number of backups attempted
    #  * number of backups with warnings
    #  * number of backups with errors (failed)
    #  * plus any additional text provided by the caller
    #
    # @return None
    def send_overall_status(self):
        svc.log.check(self.overallrc == 0, f'Overall rc: {self.overallrc}')

        # TODO: add a callback?
        # needs_commit = self._check_commits()
        status = self._get_status()

        desc = ''
        elapsed = time.time() - self._start_time
        desc += time.strftime('%H:%M:%S ', time.gmtime(elapsed))
        desc += f'overallrc={self.overallrc}; '
        desc += f'done:{self.backups_done} warns:{self.backups_warn} failed:{self.backups_failed}; '
        desc += self._notify_desc_extra
        self.notify(status, desc)

    # ---------------------
    ## add a clause to the notification description
    #
    # @param clause  the additional text to add
    # @return None
    def add_to_desc(self, clause):
        self._notify_desc_extra += clause

    # ---------------------
    ## get the status based on the backup warnings and errors
    #
    # @return (str) the status text
    def _get_status(self):
        status = 'ok'
        if self.backups_warn > 0:
            status = 'warn'
        if self.backups_failed > 0:
            status = 'err'
        return status

    # ---------------------
    ## send a notification of the final backup status.
    #
    # @param status  the overall status of the backup; typically "ok", "warn" or "err"
    # @param desc    additional details to report
    # @return None
    def notify(self, status, desc):
        self.client.notify(self.tag, status, desc)
        # e.g. of not using notify()
        # source = OsSpecific.hostname
        # event = f'base {self.tag}'
        # svc.log.line(f'notification: {source} {event} {status} {desc}')

    # ---------------------
    ## safely copy a file from src to dst
    #
    # @param src   the source path to the file
    # @param dst   the destination path
    # @return None
    def safe_copy(self, src, dst):
        src = os.path.expanduser(src)
        if os.path.exists(src):
            shutil.copy2(src, dst)

    # === get packages and various file content

    # ---------------------
    ## get various package inventories.
    # This is useful if a PC breaks. These inventories can be used to identify missing
    # packages for the OS, ruby, pip, also the crontab and fstab configurations
    #
    # @param dst_root   where to store the gathered files
    # @return None
    def get_packages(self, dst_root):
        svc.log.highlight(f'{self.tag}: {OsSpecific.os_name} get_packages')
        self.get_os_packages(dst_root)
        self.get_ruby_gems(dst_root)
        self.get_pip_modules(dst_root)

        self.get_crontab(dst_root)
        self.get_fstab(dst_root)

    # ---------------------
    ## get OS packages.
    #  * windows/MSYS2: uses pacman
    #  * macos        : uses brew
    #  * ubuntu       : uses apt and snap
    #
    # @param dst_root   where to store the gathered files
    # @return None
    def get_os_packages(self, dst_root):
        svc.log.line(f'{self.tag}: get_os_packages')
        name = 'dpkg'
        if OsSpecific.os_name == 'win':
            rc = self.get_content(dst_root, name, 'pacman -Q')
            svc.log.check(rc == 0, ' - get pacman list')
        elif OsSpecific.os_name == 'macos':
            rc = self.get_content(dst_root, name, '/opt/homebrew/bin/brew list --versions')
            svc.log.check(rc == 0, ' - get brew list')
        elif OsSpecific.os_name == 'ubuntu':
            rc = self.get_content(dst_root, name, 'apt list --installed')
            svc.log.check(rc == 0, ' - get pkg list')

            rc = self.get_content(dst_root, 'snap', 'snap list --color=never --unicode=never')
            svc.log.check(rc == 0, ' - get snap list')

    # ---------------------
    ## get ruby gem inventory.
    #
    # @param dst_root   where to store the gathered file
    # @return None
    def get_ruby_gems(self, dst_root):
        name = 'gem'
        rc = self.get_content(dst_root, name, 'gem list')
        svc.log.check(rc == 0, f' - get {name} list')

    # ---------------------
    ## get python pip inventory.
    #
    # @param dst_root   where to store the gathered file
    # @return None
    def get_pip_modules(self, dst_root):
        rc = 0
        name = 'pip3'
        if OsSpecific.os_name == 'win':
            # python3 -m pip list >"$dst_root/${THIS}_pip3_list.txt" 2>&1
            # TODO need source directory for python3
            rc = self.get_content(dst_root, name, 'python3 -m pip list')
        elif OsSpecific.os_name == 'macos':
            rc = self.get_content(dst_root, name, '/opt/homebrew/bin/python3 -m pip list')
        elif OsSpecific.os_name == 'ubuntu':
            rc = self.get_content(dst_root, name, '/usr/bin/python3 -m pip list')

        svc.log.check(rc == 0, ' - get pip list')

    # ---------------------
    ## get inventory content using the given bash command
    #
    # @param dst_root   where to store the gathered file
    # @param name       the name of the content e.g. pip3, ruby, etc.
    # @param bash_cmd   the bash command that gathers the current content
    # @return rc (return code)
    def get_content(self, dst_root, name, bash_cmd):
        dst = os.path.join(dst_root, f'{self.this}_{name}_list.txt')
        cmd = f'{bash_cmd} >"{dst}" 2>&1'
        rc, _ = OsSpecific.run_cmd(cmd, print_cb=self.print_cb)
        return rc

    # ---------------------
    ## get current crontab info
    #
    # @param dst_root   where to store the gathered file
    # @return rc (return code)
    def get_crontab(self, dst_root):
        bash_cmd = 'crontab -l'
        dst = os.path.join(dst_root, f'{self.this}_crontab.txt')
        cmd = f'{bash_cmd} >"{dst}" 2>&1'
        rc, _ = OsSpecific.run_cmd(cmd, print_cb=self.print_cb)
        return rc

    # ---------------------
    ## get current fstab info
    # note: skipped on macos since it does not normally use fstab
    #
    # @param dst_root   where to store the gathered file
    # @return rc (return code)
    def get_fstab(self, dst_root):
        if OsSpecific.os_name == 'macos':
            # macs don't use fstab
            return 0

        bash_cmd = 'cat /etc/fstab'
        dst = os.path.join(dst_root, f'{self.this}_fstab.txt')
        cmd = f'{bash_cmd} >"{dst}" 2>&1'
        rc, _ = OsSpecific.run_cmd(cmd, print_cb=self.print_cb)
        return rc

    # ---------------------
    ## set base rsync options
    #
    # @return None
    def opts_set_base(self):
        self.opts += '-avhb '
        if OsSpecific.os_name != 'macos':
            # TODO figure out how to create dst path in macos
            self.opts += '--mkpath '  # _      create full dst path
        # self._opts += '--progress '  # _     show progress ; too many lines
        self.opts += '--stats '  # _           show stats at the end of the run
        self.opts += '--delete '  # _          delete any file in the dst if they don't exist in the src
        self.opts += '--delete-excluded '  # _ delete and files/dir named by --exclude
        self.opts += '--exclude node_modules '
        self.opts += '--exclude bower_components '
        self.opts += '--exclude .git '
        self.opts += '--exclude .hg '
        self.opts += '--exclude __pycache__ '
        self.opts += '--exclude .pytest_cache '
        self.opts += '--exclude .ruff_cache '
        self.opts += '--exclude *~ '

    # ---------------------
    ## set additional rsync exclusions for the /etc directory
    #
    # @param other_exclude  current options
    # @return updated options
    def opts_set_etc(self, other_exclude):
        other_exclude += '--exclude *- '
        other_exclude += '--exclude apparmor.d '
        other_exclude += '--exclude apt/auth.conf.d/90ubuntu-advantage '
        other_exclude += '--exclude audit '
        other_exclude += '--exclude brltty '
        other_exclude += '--exclude brlapi.key '
        other_exclude += '--exclude cloud/cloud.cfg.d/90-installer-network.cfg '
        other_exclude += '--exclude cloud/cloud.cfg.d/99-installer.cfg '
        other_exclude += '--exclude credstore.encrypted '
        other_exclude += '--exclude credstore '
        other_exclude += '--exclude cups '
        other_exclude += '--exclude docker/key.json '
        other_exclude += '--exclude default/cacerts '
        other_exclude += '--exclude fwupd '
        other_exclude += '--exclude fwupd/fwupd.conf '
        other_exclude += '--exclude gshadow '
        other_exclude += '--exclude iscsi '
        other_exclude += '--exclude lvm '
        other_exclude += '--exclude multipath '
        other_exclude += '--exclude NetworkManager '
        other_exclude += '--exclude netplan '
        other_exclude += '--exclude netplan/50-cloud-init.yaml '
        other_exclude += '--exclude polkit-1 '
        other_exclude += '--exclude .pwd.lock '
        other_exclude += '--exclude profile.d/debuginfod.csh '
        other_exclude += '--exclude profile.d/debuginfod.sh '
        other_exclude += '--exclude ppp '
        other_exclude += '--exclude rsyncd.passwd '
        other_exclude += '--exclude shadow '
        other_exclude += '--exclude shadow.org '
        other_exclude += '--exclude ssl/private '
        other_exclude += '--exclude sssd '
        other_exclude += '--exclude ssh '
        other_exclude += '--exclude sudoers '
        other_exclude += '--exclude sudoers.d/README '
        other_exclude += '--exclude security/opasswd '
        other_exclude += '--exclude ufw '
        other_exclude += '--exclude vmware '
        return other_exclude
