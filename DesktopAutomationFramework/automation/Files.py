import os
from ..framework.Decorators.AutomationDecorator import AutomationDecorator
from send2trash import send2trash


class files:
    @AutomationDecorator
    @staticmethod
    def listFolderFiles(path: str) -> list[str]:
        path = os.path.expandvars(path)
        return os.listdir(path)

    @AutomationDecorator
    @staticmethod
    def deleteAllInsideFolder(path: str):
        path = os.path.expandvars(path)
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))

    @AutomationDecorator
    @staticmethod
    def exists(path: str) -> bool:
        """
        Check if a file or folder exists
        """
        path = os.path.expandvars(path)
        return os.path.exists(path)

    @AutomationDecorator
    @staticmethod
    def delete(*paths: str):
        deleted = []
        for path in paths:
            expanded_path = os.path.expandvars(path)
            try:
                send2trash(expanded_path)
                deleted.append(expanded_path)
            except Exception as e:
                deleted_count = len(deleted)
                deleted_summary = f" {deleted_count} earlier path(s) were already deleted." if deleted_count > 0 else ""
                raise Exception(
                    f"Could not delete '{expanded_path}'.{deleted_summary} {str(e)}"
                )

    @AutomationDecorator
    @staticmethod
    def createFile(path: str, *content: str):
        """
        Create a file and write lines to it
        ex: createFile("C:\\folder\\myfile.py", "line1", "line2", "line3")
        """
        path = os.path.expandvars(path)
        with open(path, "w") as file:
            file.writelines(content)
            pass

    @AutomationDecorator
    @staticmethod
    def createFolder(path: str):
        path = os.path.expandvars(path)
        os.makedirs(path)

    @AutomationDecorator
    @staticmethod
    def read(path: str) -> str:
        path = os.path.expandvars(path)
        with open(path, "r") as file:
            return file.read()

    @AutomationDecorator
    @staticmethod
    def readLines(path: str) -> list[str]:
        path = os.path.expandvars(path)
        with open(path, "r") as file:
            return file.readlines()

    @AutomationDecorator
    @staticmethod
    def show(path: str):
        path = os.path.expandvars(path)
        os.startfile(path)
