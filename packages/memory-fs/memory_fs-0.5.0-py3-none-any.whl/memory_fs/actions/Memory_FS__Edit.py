from typing                                             import List
from memory_fs.schemas.Schema__Memory_FS__File          import Schema__Memory_FS__File
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage.Memory_FS__Storage               import Memory_FS__Storage
from osbot_utils.helpers.safe_str.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Memory_FS__Edit(Type_Safe):
    storage     : Memory_FS__Storage

    def clear(self) -> None:                                                                    # Clear all files and directories
        self.storage.files       ().clear()         # todo: refactor this logic to storage
        self.storage.content_data().clear()

    # todo: see if we need this, since now that we have multiple paths support, the logic in the copy is more complicated
    # def copy(self, source      : Safe_Str__File__Path ,                                        # Copy a file from source to destination
    #                destination : Safe_Str__File__Path
    #           ) -> bool:
    #     if source not in self.storage.files():
    #         return False
    #
    #     file = self.storage.file(source)
    #     self.save(destination, file)
    #
    #     # Also copy content if it exists
    #     if source in self.storage.content_data():                                               # todo: need to refactor the logic of the files and the support files
    #         self.save_content(destination, self.storage.file__content(source))
    #
    #     return True

    def delete(self, path : Safe_Str__File__Path                                               # Delete a file at the given path
                ) -> bool:
        if path in self.storage.files():
            del self.storage.files()[path]                                                     # todo: this needs to be abstracted out in the storage class
            return True
        return False

    def delete_content(self, path : Safe_Str__File__Path                                       # Delete content at the given path
                        ) -> bool:
        if path in self.storage.content_data():
            del self.storage.content_data()[path]                                               # todo: this needs to be abstracted out in the storage class
            return True
        return False

    # todo: see if we need this, since now that we have multiple paths support, the logic in the move is more complicated
    # def move(self, source      : Safe_Str__File__Path ,                                        # Move a file from source to destination
    #                destination : Safe_Str__File__Path
    #           ) -> bool:
    #     if source not in self.storage.files():
    #         return False
    #
    #     file = self.storage.file(source)
    #     self.save(destination, file)
    #     self.delete(source)
    #
    #     # Also move content if it exists
    #     if source in self.storage.content_data():
    #         self.save_content(destination, self.storage.file__content(source))
    #         self.delete_content(source)
    #
    #     return True

    # todo: find a better name for this method and file ('fs' is okish, maybe 'config')
    def save(self, file_config: Schema__Memory_FS__File__Config,
                   file       : Schema__Memory_FS__File             # refactor out the metadata from this , and put it on a separate file we then would not need this Schema__Memory_FS__File class
              ) -> List[Safe_Str__File__Path]:
        files_to_save = []
        full_file_name = f"{file_config.file_name}.{file_config.file_type.file_extension}"
        if file_config.file_paths:                                  # if we have file_paths define mapp them all
            for file_path in file_config.file_paths:
                content_path   = Safe_Str__File__Path(f"{file_path}/{full_file_name}")
                full_file_path = Safe_Str__File__Path(content_path + ".fs.json")                                                    # todo: refactor this into a better location

                files_to_save.append(full_file_path)
        else:
            files_to_save.append(full_file_name  + ".fs.json")                   # if not, save on the root  # todo: fix this hardcoding of ".fs.json"

        for file_to_save in files_to_save:
            self.storage.files()[file_to_save] = file                        # Store the file # todo: this needs to be moved into the storage class

        return files_to_save

    # todo: need to updated the metadata file save the length in the metadata
    def save_content(self, file_config: Schema__Memory_FS__File__Config,
                           content : bytes
              ) -> List[Safe_Str__File__Path]:
        files_to_save  = []
        full_file_name = f"{file_config.file_name}.{file_config.file_type.file_extension}"      # todo: refactor this into a method or class focused on creating the file name (one for example that takes into account when the file_type.file_extension is not set)
        if file_config.file_paths:
            for file_path in file_config.file_paths:
                content_path   = Safe_Str__File__Path(f"{file_path}/{full_file_name}")
                files_to_save.append(content_path)
        else:
            files_to_save.append(full_file_name)
        for file_to_save in files_to_save:
            self.storage.content_data()[file_to_save] = content                                          # Store the file # todo: this needs to be moved into the storage class
        return files_to_save
