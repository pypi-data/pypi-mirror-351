from cmflib import cmf
import subprocess
import os
import time
import asyncio
import tarfile
from pathlib import Path
from datetime import datetime
import threading
import shutil
from waggle.plugin import Plugin
from waggle.plugin import get_timestamp
import logging

logger = logging.getLogger(__name__)



class cmfsage:
    def __init__(self,pipeline_name,pipeline_file,model_path,result_path,git_remote_url,archiving=True,logging_interval=5):
        self.pipeline_name= pipeline_name
        self.pipeline_file= pipeline_file
        self.model_path= model_path
        self.result_path= result_path
        self.git_remote_url= git_remote_url
        self.archiving= archiving #if we are archiving the result, we put the arvhive file into the logging queue otherwise we put the result intot the logging queue
        self.logging_interval= logging_interval
        self.monitoring_interval=0.05
        self.stop_event=None

    def check_path(self):
        if os.path.isdir(self.result_path):
            return self.result_path, "dir"
        elif os.path.isfile(self.result_path):
            return os.path.dirname(self.result_path), "file"
        else:
            raise ValueError(f"Invalid result path: {self.result_path}")
    
    def relative_path(path):

        return os.path.relpath(path)
    
    async def setup(self):
        '''Check the path is diretory or file'''
        '''If it is a directory, we will use the directory as the result path'''
        '''If it is a file, we will use the parent directory as the result path'''
        
        #check if archiving
        if self.archiving:
            self.result_archiving_path="result_archive"
            os.makedirs(self.result_archiving_path, exist_ok=True)
            
        #result path check
        self.result_path, self.result_type = self.check_path(self.result_path)

        self.result_archiving_queue= asyncio.Queue()
        self.cmf_logging_queue = asyncio.Queue() 
        self.cmf_archive_queue = asyncio.Queue()
        self.cmf_upload_queue = asyncio.Queue()

        await asyncio.gather(
            self.monitor_and_archive(self.result_path, self.cmf_logging_queue,self.result_archiving_queue),
            self.log_result_archives(self.pipeline_name, self.pipeline_file, self.model_path,self.logging_queue, self.cmf_archive_queue,self.git_remote_url),
            self.cmf_archive(self.pipeline_file, self.cmf_archive_queue,self.cmf_upload_queue),
            self.cmf_upload(self.cmf_upload_queue)
        )

        
    def clear_folder(self):
        dvc_path=".dvc"
        cmf_artifacts="cmf_artifacts"
        if os.path.exists(dvc_path):
            
            shutil.rmtree(dvc_path)
            #print(f"Removed {dvc_path}")
            logger.info(f"Removed {dvc_path}")
        if os.path.exists(cmf_artifacts):
            shutil.rmtree(cmf_artifacts)
            #print(f"Removed {cmf_artifacts}")
            logger.info(f"Removed {cmf_artifacts}")
        if os.path.exists(self.pipeline_name):
            os.remove(self.pipeline_name)
            #print(f"Removed {pipeline_name}")
            logger.info(f"Removed {self.pipeline_name}")
        if os.path.exists(self.model_path+".dvc"):
            os.remove(self.model_path+".dvc")
            #print(f"Removed {model_path}.dvc")
            logger.info(f"Removed {self.model_path}.dvc")
    
    async def cmf_archive(self):
        """Archive files from .dvc/cache, cmf_artifacts, and other sources, and add them to the upload queue."""
        os.makedirs(self.cmf_archive_path, exist_ok=True)
        while not (self.stop_event and self.stop_event.is_set()):
            if self.cmf_archive_queue.empty():
                await asyncio.sleep(1)
                continue

            # Archive everything in the .dvc/cache folder
            while not self.cmf_archive_queue.empty():
                dvc_path = ".dvc/cache"
                cmf_artifacts = "cmf_artifacts"

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                tar_path = os.path.join(self.cmf_archive_path, f"cmf_archive_{timestamp}.tar.gz")
                with tarfile.open(tar_path, "w:gz") as tar:
                    # Add .dvc/cache folder
                    if os.path.exists(dvc_path):
                        tar.add(dvc_path, arcname=".dvc/cache")

                    # Add cmf_artifacts folder
                    if os.path.exists(cmf_artifacts):
                        tar.add(cmf_artifacts, arcname="cmf_artifacts")

                    # Add pipeline_name file
                    if os.path.exists(self.pipeline_path):
                        tar.add(self.pipeline_path, arcname=self.pipeline_path)

                    # Add files from cmf_archive_queue
                    while not self.cmf_archive_queue.empty():
                        file_path = await self.cmf_archive_queue.get()
                        if os.path.exists(file_path):
                            tar.add(file_path, arcname=file_path)
                        self.cmf_archive_queue.task_done()
                await self.cmf_upload_queue.put(tar_path)  
    
    async def log_result_archives(self):
        while True:
            try:
                tar_paths= [] 
                while not self.cmf_logging_queue.empty():
                    tar_path= await self.cmf_logging_queue.get()  # Wait for a new archive file
                    tar_paths.append(tar_path)
                    self.cmf_logging_queue.task_done()
                if tar_paths:
                    self.clear_folder()
                    try:
                        
                        metawriter = cmf.Cmf(self.pipeline_file, self.pipeline_name)
                        stage_name = "inference"
                        execution_name = "image inferencing"
                        _ = metawriter.create_context(pipeline_stage=str(stage_name))
                        _ = metawriter.create_execution(execution_type=str(execution_name))
                        _ = metawriter.log_model(self.relative_path(self.model_path), event="input")
                        
                        for tar_path in tar_paths:
                            print(tar_path)
                            _ = metawriter.log_dataset(tar_path, event="output")
                        logger.info("CMF logging completed successfully.")
                    except Exception as e:
                        print(f"Error during CMF logging: {{e}}")
                    
                    for tar_path in tar_paths:
                        tar_dvc_path=tar_path+".dvc"
                        await self.cmf_archive_queue.put(tar_dvc_path)
                        await self.cmf_archive_queue.put(tar_path)
                    model_dvc_path=self.model_path+".dvc"
                    await self.cmf_archive_queue.put(self.model_path)
                    await self.cmf_archive_queue.put(model_dvc_path)    
                await asyncio.sleep(self.logging_interval) #make it variable

            except Exception as e:
                print(f"Error in cmf_logging: {e}")
                await asyncio.sleep(self.logging_interval)         

    async def cmf_upload(self):
        while True:
            try:
                while not self.cmf_upload_queue.empty():
                    upload_path = await self.cmf_upload_queue.get()
                    #print(f"Uploading {upload_path} to waggle sensor...")
                    logger.info(f"Uploading {upload_path} to waggle sensor...")
                    try:
                        with Plugin() as plugin:
                            plugin.upload_file(upload_path, timestamp=get_timestamp())
                    except Exception as e:
                            print(f"waggle upload failed for {upload_path}: {e}")
                            continue
                    self.cmf_upload_queue.task_done()
                await asyncio.sleep(12)
            except Exception as e:
                #print(f"Error in cmf_upload: {e}")
                logger.error(f"Error in cmf_upload: {e}")
                await asyncio.sleep(self.logging_interval)       

    async def monitor_and_archive(self):
        async def monitor_file(self):
            #make duplicate of the file with timestamp
            #check if the file is changed
            last_mtime=None
            while True:
                if os.path.exists(self.result_path):
                    mtime = os.path.getmtime(self.result_path)
                if mtime != last_mtime:
                    last_mtime = mtime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dst_path =  f"{timestamp}_{self.result_path}"
                    shutil.copy2(self.result_path, dst_path) #what if the copy is slower than interval? 
                    if self.archiving:
                        await self.result_archiving_queue.put(dst_path)
                    else:
                        await self.cmf_logging_queue.put(dst_path)
        async def monitor_dir(self):
            #check if there is new files in the directory
            seen_files = set()
            while True:
                current_files = set(Path(self.result_path))
                new_files = current_files - seen_files
                if new_files:
                    for file_path in new_files:
                        logger.info(f"New file detected: {file_path}")
                        seen_files.add(file_path)
                        if self.archiving:
                            await self.result_archiving_queue.put(file_path)
                        else:
                            await self.cmf_logging_queue.put(file_path)

        if self.result_type== "file":
            await monitor_file()
        if self.result_type== "dir":    
            await monitor_dir()
    
                        
        
    def cmf_logging(self):
        metawriter= cmf.Cmf(self.pipeline_file, self.pipeline_name)
        stage_name= "inference"
        execution_name= "run inference"
        _= metawriter.create_context(pipeline_stage=str(stage_name))
        _= metawriter.create_execution(execution_type=str(execution_name))
        _= metawriter.log_model(self.relative_path(self.model_path), event="input")
        _= metawriter.log_dataset(self.relative_path(self.result_path), event="output")
        logger.info(f"CMF logging completed successfully.")




    def cmf_init(self):
        '''This function initializes the CMF environment in every cmf logging window'''
        '''After removing previous dvc cache and cmf sqlite,it creates new dvc cache and sqlite'''
        #print(f"cmf_init: {self.git_remote_url}")
        logger.info(f"cmf_init: {self.git_remote_url}")
        

        subprocess.run([
            "cmf", "init", "local",
            "--path", ".",
            "--cmf-server-url", "http://127.0.0.1:80",
            "--git-remote-url", self.git_remote_url
        ])
    

    def schedule(self):
        '''if we are archiving inferencing result, we need to create the result archiving path'''
        '''if there is no archiving of the result, we will simply do the cmf logging on the inference results'''
        '''we will set default window to 4 seconds if otherwise not specified'''
        
        if self.archiving:
            self.result_archiving_path= "result_archiving"
            os.makedirs(self.result_archiving_path, exist_ok=True)
            


    def cmf_logging_thread(self):
        #print(f"Starting CMF logging thread of {pipeline_name} whose mlmd file name is {pipeline_file} with git_remote_url: {git_remote_url}. The model path is {model_path} and the result dir is {result_dir}")   
        logger.info(f"Starting CMF logging thread of {self.pipeline_name} whose mlmd file name is {self.pipeline_file} with git_remote_url: {self.git_remote_url}. The model path is {self.model_path} and the result dir is {self.result_dir}")
        def run_cmf_logging_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.task_scheduler(self.pipeline_name, self.pipeline_file,self.model_path,self.result_dir, self.git_remote_url))
        thread= threading.Thread(target=run_cmf_logging_in_thread,daemon=True)
        thread.start()
        return thread       
           
    def cmf_logging_thread(self):
        #this thread returns ending to the main thread
        logging.info("CMF loggging thread starts")
        return self.cmf_logging_thread




if __name__ == "__main__":
    #We define cmf_sage watchdog to keep track of the inference result
    #User needs to provide: 
    '''Pipeline name: What's the pipeline to trace'''
    '''Pipeline file: The mlmd file name, mlmd file be default'''
    '''Model path: The location to the model'''
    '''Result path: The location to the inference result'''
    '''Git remote url: The git remote url to the AI repository'''
    params = {
        "pipeline_name": "wildfire-classification",
        "pipeline_file": "mlmd",
        "model_path": "model.tflite",
        #this can be a directory or a file
        #if this is a file, we will use timestamp to track the files changed. Apply higher monitoring frequency
        #if this is a directory, we will keep track of the files changed in the directory. Apply lower monitoring frequency
        "result_path": "image.jpg",
        "git_remote_url": "https://github.com/hpeliuhan/cmf_proxy_demo.git",
        "archiving": True,
        "logging_window": 4
    }

    cmf_logger = cmfsage(**params)
