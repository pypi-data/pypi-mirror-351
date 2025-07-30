from typing                                             import Dict
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from memory_fs.actions.Memory_FS__Edit                  import Memory_FS__Edit
from memory_fs.actions.Memory_FS__Load                  import Memory_FS__Load
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.helpers.Safe_Id                        import Safe_Id
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.decorators.methods.cache_on_self       import cache_on_self
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class Memory_FS__Delete(Type_Safe):
    storage     : Memory_FS__Storage

    @cache_on_self
    def memory_fs__edit(self):
        return Memory_FS__Edit(storage=self.storage)

    @cache_on_self
    def memory_fs__load(self):
        return Memory_FS__Load(storage=self.storage)

    @cache_on_self
    def memory__fs_storage(self):
        return Memory_FS__Storage(file_system=self.storage.file_system)

    def delete(self, file_config : Schema__Memory_FS__File__Config                  # Delete file from all configured paths
                ) -> Dict[Safe_Id, bool]:
        files_deleted = []

        for file_path in file_config.file_paths:
            content_path  = Safe_Str__File__Path(f"{file_path}/{file_config.file_name}.{file_config.file_type.file_extension}")
            metadata_path = Safe_Str__File__Path(content_path + ".fs.json")                   # todo: refactor this into a separate class (which will handle the case of the ".fs.json" extension)

            if self.memory_fs__edit().delete_content(content_path):
                files_deleted.append(content_path)

            if self.memory_fs__edit().delete(metadata_path):
                files_deleted.append(metadata_path)

        return files_deleted