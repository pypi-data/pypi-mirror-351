from typing                                             import Optional, Any
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.actions.Memory_FS__Data                  import Memory_FS__Data
from memory_fs.actions.Memory_FS__Deserialize           import Memory_FS__Deserialize
from memory_fs.actions.Memory_FS__Paths                 import Memory_FS__Paths
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from memory_fs.schemas.Schema__Memory_FS__File          import Schema__Memory_FS__File
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class Memory_FS__Load(Type_Safe):
    storage     : Memory_FS__Storage

    @cache_on_self
    def memory_fs__data(self):
        return Memory_FS__Data(storage=self.storage)

    @cache_on_self
    def memory_fs__deserialize(self):
        return Memory_FS__Deserialize(storage=self.storage)

    @cache_on_self
    def memory_fs__paths(self):
        return Memory_FS__Paths()


    def load(self, file_config : Schema__Memory_FS__File__Config  # Load file from the appropriate path based on config
              ) -> Optional[Schema__Memory_FS__File]:
        full_file_name = Safe_Str__File__Path(f"{file_config.file_name}.{file_config.file_type.file_extension}.fs.json")
        if not file_config.file_paths:
            return self.memory_fs__data().load(full_file_name)
        for file_path in file_config.file_paths:                        # Try each handler in order until we find the file              # todo: see if we need to add back the logic to have a default file path variable
            full_file_path = Safe_Str__File__Path(f"{file_path}/{full_file_name}")
            file           = self.memory_fs__data().load(full_file_path)
            if file:
                return file

        return None

    def load_content(self, file_config : Schema__Memory_FS__File__Config  # Load content for a file
                      ) -> Optional[bytes]:
        for file_path in file_config.file_paths:                        # Try each handler in order until we find the file  # todo: see if we need to add back the logic to have a default file path variable
            full_file_path = Safe_Str__File__Path(f"{file_path}/{file_config.file_name}.{file_config.file_type.file_extension}")
            content_bytes  = self.memory_fs__data().load_content(full_file_path)
            if content_bytes:
                return content_bytes
        return None

        # First load the metadata to get content path
        file = self.load_content(file_config)
        if not file:
            return None

        # Get the content path from metadata
        if file.metadata.content_paths:
            # If there's a default handler, try its content path first
            if file_config.default_handler and file_config.default_handler.name in file.metadata.content_paths:
                content_path = file.metadata.content_paths[file_config.default_handler.name]
                content = self.memory_fs__data().load_content(content_path)
                if content:
                    return content

            # Otherwise try any available content path
            for content_path in file.metadata.content_paths.values():
                content = self.memory_fs__data().load_content(content_path)
                if content:
                    return content

        return None

    def load_data(self, file_config : Schema__Memory_FS__File__Config  # Load and deserialize file data
                  ) -> Optional[Any]:
        # Load raw content
        content_bytes = self.load_content(file_config)
        if not content_bytes:
            return None

        # Deserialize based on file type
        return self.memory_fs__deserialize()._deserialize_data(content_bytes, file_config.file_type)
