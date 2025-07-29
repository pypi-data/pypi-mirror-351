import os
import mimetypes
import re
import subprocess

from kabaret import flow
from kabaret.flow.object import _Manager

from libreflow.baseflow.file import RenderAEPlayblast,SelectAEPlayblastRenderMode,TrackedFile,TrackedFolder,FileRevisionNameChoiceValue,MarkImageSequence,WaitProcess

class RenderQualityChoiceValue(flow.values.ChoiceValue):
    CHOICES = ['Preview','Final']

class AfterFX_Playblast_Comp(SelectAEPlayblastRenderMode):

    # Action startup with parameter selection

    _MANAGER_TYPE = _Manager

    ICON = ('icons.libreflow', 'afterfx')

    render_quality  = flow.Param("Preview",RenderQualityChoiceValue)

    def get_buttons(self):
        return ['Render', 'Cancel']

    def run(self,button):
        if button == 'Cancel':
            return

        # Get AfterEffects templates configured in current site
        site = self.root().project().get_current_site()
        render_settings = (site.ae_render_settings_templates.get() or {}).get(
            self.render_settings.get()
        )
        output_module = (site.ae_output_module_templates.get() or {}).get(
            self.output_module.get()
        )
        audio_output_module = site.ae_output_module_audio.get()

        if button == 'Render':
            render_action = self._file.render_ae_playblast
            render_action.render_quality.set(self.render_quality.get())
            render_action.revision.set(self.revision.get())
            render_action.render_settings.set(render_settings)
            render_action.output_module.set(output_module)
            render_action.audio_output_module.set(audio_output_module)
            render_action.start_frame.set(self.start_frame.get())
            render_action.end_frame.set(self.end_frame.get())

            if (self.start_frame.get() is not None or self.end_frame.get() is not None) and self._has_render_folder():
                return self.get_result(next_action=self._file.select_ae_playblast_render_mode_page2.oid())
                
            render_action.run('Render')   


class AfterFX_Render_Playblast(RenderAEPlayblast):

    # Render img sequence in after fx

    render_quality = flow.Param()
    
    def _render_wait(self, folder_name, revision_name, render_pid, export_audio_pid):
        render_wait = self._file.final_render_wait
        render_wait.folder_name.set(folder_name)
        render_wait.revision_name.set(revision_name)
        render_wait.wait_pid(render_pid)
        render_wait.wait_pid(export_audio_pid)
        render_wait.run(None)

    def run(self,button):
        if button == 'Cancel':
            return
        
        revision_name = self.revision.get()

        # Render image sequence
        ret = self._render_image_sequence(
            revision_name,
            self.render_settings.get(),
            self.output_module.get(),
            self.start_frame.get(),
            self.end_frame.get(),
        )
        render_runner = self.root().session().cmds.SubprocessManager.get_runner_info(
            ret['runner_id']
        )
        # Export audio
        ret = self._export_audio(
            revision_name,
            self.audio_output_module.get()
        )
        export_audio_runner = self.root().session().cmds.SubprocessManager.get_runner_info(
            ret['runner_id']
        )

        folder_name = self._file.name()[:-len(self._file.format.get())]
        folder_name += 'render'

        if self.render_quality.get() == 'Preview':
            print('RENDER QUALITY PREVIEW')
            # Configure and start image sequence marking for preview output
            self._mark_image_sequence(
                folder_name,
                revision_name,
                render_pid=render_runner['pid'],
                export_audio_pid=export_audio_runner['pid']
            )
        
        if self.render_quality.get() == 'Final':
            print('RENDER QUALITY FINAL')
            # Configure and start image sequence conversion for final output
            self._render_wait(
                folder_name,
                revision_name,
                render_pid=render_runner['pid'],
                export_audio_pid=export_audio_runner['pid']
            )


class Final_Render_Waiting(WaitProcess):

    # Image sequence conversion for Final output

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)

    folder_name = flow.Param()
    revision_name = flow.Param()

    def get_run_label(self):
        return 'Convert image sequence'

    def _ensure_file_revision(self, name, revision_name):
        mng = self.root().project().get_task_manager()
        default_files = mng.get_task_files(self._task.name())

        # Find matching default file
        match_dft_file = False
        for file_mapped_name, file_data in default_files.items():
            # Get only files
            if '.' in file_data[0]:
                base_name, extension = os.path.splitext(file_data[0])
                if name == base_name:
                    extension = extension[1:]
                    path_format = file_data[1]
                    match_dft_file = True
                    break
        
        # Fallback to default mov container
        if match_dft_file is False:
            extension = 'mov'
            path_format = mng.get_task_path_format(self._task.name()) # get from default task
        
        mapped_name = name + '_' + extension
        
        if not self._files.has_mapped_name(mapped_name):
            file = self._files.add_file(
                name, extension, tracked=True,
                default_path_format=path_format
            )
        else:
            file = self._files[mapped_name]
        
        if not file.has_revision(revision_name):
            revision = file.add_revision(revision_name)
            file.set_current_user_on_revision(revision_name)
        else:
            revision = file.get_revision(revision_name)
        
        file.file_type.set('Outputs')
        file.ensure_last_revision_oid()
        
        return revision

    def _get_first_image_path(self, revision):
        img_folder_path = revision.get_path()
        
        for f in os.listdir(img_folder_path):
            file_path = os.path.join(img_folder_path, f)
            file_type = mimetypes.guess_type(file_path)[0].split('/')[0]
            
            if file_type == 'image':
                return file_path
        
        return None
    
    def _get_audio_path(self,folder_name):
        if any("_aep" in file for file in self._files.mapped_names()):
            scene_name = folder_name.replace('_render', '_aep')
        else : 
            scene_name = re.search(r"(.+?(?=_render))", folder_name).group()
            
        if not self._files.has_mapped_name(scene_name):
            # Scene not found
            return None
            
        return self._files[scene_name].export_ae_audio.get_audio_path()

    
    def launcher_exec_func_kwargs(self):
        return dict(
            folder_name=self.folder_name.get(),
            revision_name=self.revision_name.get()
        )
    
    def _do_after_process_ends(self, *args, **kwargs):
        self.root().project().ensure_runners_loaded()
        sequence_folder = self._files[kwargs['folder_name']]

        rev = sequence_folder.get_revision(kwargs['revision_name'])
        path = self._get_first_image_path(rev)
        input_path = path.replace('0000.png', r'%04d.png')

        print('INPUT_PATH = ' + input_path)

        output_name= kwargs['folder_name'].replace('_render', '_movie')
        output_rev = self._ensure_file_revision(output_name,kwargs['revision_name'])
        output_path = output_rev.get_path()

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))

        print('OUPUT PATH = ' + output_path)

        audio_path = self._get_audio_path(kwargs['folder_name'])

        print('AUDIO PATH = ' + audio_path)

        process = subprocess.run(f'ffmpeg -y -r 25 -i {input_path} -i {audio_path} -c:a aac -map 0:0 -map 1:0 -c:v prores_ks -profile:v 3 -vendor apl0 -bits_per_mb 8000 -pix_fmt yuv422p10le {output_path}' , check=False, shell=True)

        print(f"COMMAND:\n{' '.join(process.args)}")
        print(f"STDERR: {repr(process.stderr)}")
        print(f'STDOUT: {process.stdout}')
        print(f'RETURN CODE: {process.returncode}')
        
        if not os.path.exists(output_path):
            self.message.set((
                "<h2>Upload playblast to Kitsu</h2>"
                "<font color=#FF584D>File conversion failed</font>"
            ))
            return self.get_result(close=False)



class MarkSequencePreview(MarkImageSequence):

    # Image sequence marking and conversion for preview output

    def mark_sequence(self, revision_name):
        # Compute playblast prefix
        prefix = self._folder.name()
        prefix = prefix.replace('_render', '')
        
        source_revision = self._file.get_revision(revision_name)
        revision = self._ensure_file_revision(prefix + '_preview_movie', revision_name)
        revision.comment.set(source_revision.comment.get())
        
        # Get the path of the first image in folder
        img_path = self._get_first_image_path(revision_name)
        
        # Get original file name to print on frames
        if self._files.has_mapped_name(prefix + '_aep'):
            scene = self._files[prefix + '_aep']
            file_name = scene.complete_name.get() + '.' + scene.format.get()
        else:
            file_name = self._folder.complete_name.get()
        
        self._extra_argv = {
            'image_path': img_path,
            'video_output': revision.get_path(),
            'file_name': file_name,
            'audio_file': self._get_audio_path()
        }
        
        return super(MarkImageSequence, self).run('Render')
        


def afterfx_render_playblast(parent):
    if isinstance(parent, TrackedFile) \
        and (parent.name().endswith('_aep')) \
        and (parent._task.name() == 'compositing'):
        r = flow.Child(AfterFX_Render_Playblast)
        r.name = 'render_ae_playblast'
        r.ui(hidden=True)
        return r

def afterfx_playblast_comp(parent):
    if isinstance(parent, TrackedFile) \
        and (parent.name().endswith('_aep')) \
        and (parent._task.name() == 'compositing'):
        r = flow.Child(AfterFX_Playblast_Comp)
        r.name = 'render_playblast'
        r.ui(label='Render')
        return r

def mark_sequence_preview(parent):
    if isinstance(parent, TrackedFolder) \
        and(parent._task.name() == 'compositing'):
        r = flow.Child(MarkSequencePreview)
        r.name = 'mark_image_sequence'
        r.ui(hidden=True)
        return r

def final_render_wait(parent):
    if isinstance(parent, TrackedFile) \
        and(parent._task.name() == 'compositing'):
        r = flow.Child(Final_Render_Waiting)
        r.name = 'final_render_wait'
        r.ui(hidden=True)
        return r



def install_extensions(session):
    return {
        "2h14_comp": [
            afterfx_playblast_comp,
            afterfx_render_playblast,
            mark_sequence_preview,
            final_render_wait,

        ]
    }


from . import _version
__version__ = _version.get_versions()['version']
