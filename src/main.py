import os

from dotenv import load_dotenv
import supervisely as sly
from supervisely.project.project_type import ProjectType

load_dotenv("local.env")
load_dotenv(os.path.expanduser("~/supervisely.env"))

api = sly.Api()


workspace_id = sly.env.workspace_id()

project = api.project.create(
    workspace_id,
    "Volume tutorial",
    ProjectType.VOLUMES,
    change_name_if_conflict=True,
)
print(f"Project ID: {project.id}")


dataset = api.dataset.create(project.id, "dataset_1")
print(f"Dataset ID: {dataset.id}")


# upload 1 nnrd volume as nrrd from local directory to Supervisely platform
upload_path = "src/upload/MRHead.nrrd"
nrrd_info = api.volume.upload_nrrd_serie_path(
    dataset.id,
    "NRRD_1.nrrd",
    upload_path,
    log_progress=False,
)
print(f'"{nrrd_info.name}" volume uploaded to Supervisely with ID:{nrrd_info.id}')


# upload volume as NumPy array to Supervisely platform
np_volume, meta = sly.volume.read_nrrd_serie_volume_np(upload_path)
nrrd_info_np = api.volume.upload_np(dataset.id, "Np_volume.nrrd", np_volume, meta)
print(f"Volume uploaded as NumPy array to Supervisely with ID:{nrrd_info_np.id}")


# upload list of nrrd files from local directory to Supervisely
upload_dir_path = "src/upload/folder/"
paths = ["src/upload/folder/CTACardio.nrrd", "src/upload/folder/another_folder/MRHead-1.nrrd"]
names = ["CTACardio.nrrd", "MRHead-1.nrrd"]

volume_infos = api.volume.upload_nrrd_series_paths(dataset.id, names, paths)
print(f"All volumes has been uploaded with IDs: {[x.id for x in volume_infos]}")

# upload DICOM volume from local directory to Supervisely platform
upload_dir_path = "src/upload/Dicom_files/"
series_infos = sly.volume.inspect_dicom_series(root_dir=upload_dir_path)
for serie_id, files in series_infos.items():
    item_path = files[0]
    if sly.volume.get_extension(path=item_path) is None:
        sly.logger.warn(f"Can not recognize file extension {item_path}, serie will be skipped")
        continue
    name = f"{sly.fs.get_file_name(path=item_path)}.nrrd"
    volume_info = api.volume.upload_dicom_serie_paths(
        dataset_id=dataset.id,
        name=name,
        paths=files,
        log_progress=False,
        anonymize=True,  # hide patient's name and ID before uploading to Supervisely platform
    )
    print(f"DICOM volume has been uploaded to Supervisely with ID: {volume_info.id}")


# get volume info from Supervisely platform by volume name
info_by_name = api.volume.get_info_by_name(dataset.id, name=nrrd_info.name)
print(f"Volume name: ", info_by_name.name)

# get volume info from Supervisely platform by volume id
info_by_id = api.volume.get_info_by_id(id=nrrd_info.id)
print(f"Volume name: ", info_by_id.name)

# get list of volumes from current dataset from Supervisely
volumes_list = api.volume.get_list(dataset.id)
volumes_ids = [x.id for x in volumes_list]
print(f"List of volumes`s IDs: {volumes_ids}")


# download volume from Supervisely to local directory
download_dir = "src/download/"
download_path = os.path.join(download_dir, "MRHead.nrrd")

if os.path.exists(download_path):
    os.remove(download_path)

api.volume.download_path(nrrd_info.id, download_path)

list_dir = os.listdir(download_dir)
if len(list_dir) > 0:
    print("Volume successfully downloaded.")
