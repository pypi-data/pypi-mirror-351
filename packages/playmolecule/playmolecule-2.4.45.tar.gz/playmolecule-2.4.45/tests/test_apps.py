from distutils import dir_util
from pytest import fixture
import os


@fixture
def datadir(tmpdir, request):
    """
    Fixture responsible for searching a folder with the same name of test
    module and, if available, moving all contents to a temporary directory so
    tests can use them freely.
    """
    filename = request.module.__file__
    test_dir, _ = os.path.splitext(filename)

    if os.path.isdir(test_dir):
        dir_util.copy_tree(test_dir, str(tmpdir))

    return tmpdir


def prepare(datadir):
    outdir = str(datadir.join("out"))
    scratchdir = str(datadir.join("scratch"))
    os.makedirs(outdir, exist_ok=True)
    os.makedirs(scratchdir, exist_ok=True)
    return outdir, scratchdir


# def _test_acedock(datadir):
#     from playmolecule import apps

#     outdir, scratchdir = prepare(datadir)
#     apps.acedock.v1(
#         outdir=outdir,
#         scratchdir=scratchdir,
#         protein=str(datadir.join("acedock/protein.mol2")),
#         template=str(datadir.join("acedock/templ_lig.sdf")),
#         ligands=str(datadir.join("acedock/ligands.sdf")),
#     ).run()

#     expected_files = [
#         "outlig0.sdf",
#         "outlig1.sdf",
#         "protein.pdb",
#         "rdock_err.log",
#         "rdock-grid.grd",
#         "scores.csv",
#         "template.sdf",
#     ]
#     for expf in expected_files:
#         assert os.path.exists(os.path.join(outdir, expf))


# def _test_mdrun(datadir):
#     from playmolecule import apps

#     outdir, scratchdir = prepare(datadir)
#     apps.mdrun.v1(
#         outdir=outdir,
#         scratchdir=scratchdir,
#         inputdir=str(datadir.join("mdrun/prod_alanine_dipeptide_amber")),
#     ).run()

#     expected_files = ["mdfolder/output.xtc"]
#     for expf in expected_files:
#         assert os.path.exists(os.path.join(outdir, expf))


# def _test_parameterize(datadir):
#     from playmolecule import apps

#     outdir, scratchdir = prepare(datadir)
#     apps.parameterize.v1(
#         outdir=outdir,
#         scratchdir=scratchdir,
#         molecule=str(datadir.join("parameterize/BEN.cif")),
#     ).run()

#     expected_files = [
#         "dihedral-single-point",
#         "parameters",
#         "parameters/GAFF2/arguments.txt",
#         "parameters/GAFF2/input.namd",
#         "parameters/GAFF2/MOL.cif",
#         "parameters/GAFF2/MOL.frcmod",
#         "parameters/GAFF2/MOL-orig.cif",
#         "parameters/GAFF2/MOL-orig.mol2",
#         "parameters/GAFF2/MOL.xml",
#         "parameters/GAFF2/random-search.log",
#         "parameters/GAFF2/energies.txt",
#         "parameters/GAFF2/leaprc.MOL",
#         "parameters/GAFF2/MOL.coor",
#         "parameters/GAFF2/MOL.mol2",
#         "parameters/GAFF2/MOL-orig.coor",
#         "parameters/GAFF2/MOL.pdb",
#         "parameters/GAFF2/plots",
#         "parameters/GAFF2/tleap.in",
#     ]
#     for expf in expected_files:
#         assert os.path.exists(os.path.join(outdir, expf))


# def _test_proteinprepare(datadir):
#     from playmolecule import apps

#     outdir, scratchdir = prepare(datadir)
#     apps.proteinprepare.v1(
#         outdir=outdir,
#         scratchdir=scratchdir,
#         pdbfile=str(datadir.join("proteinprepare/3ptb.pdb")),
#     ).run()

#     expected_files = ["details.csv", "output.pdb", "pka_plot.png", "web_content.pickle"]
#     for expf in expected_files:
#         assert os.path.exists(os.path.join(outdir, expf))


# def _test_shapeit(datadir):
#     from playmolecule import apps

#     outdir, _ = prepare(datadir)
#     apps.shapeit.v1(
#         outdir=outdir,
#         outname="fda_against_aspirin.sdf",
#         ref=str(datadir.join("shapeit/aspirin.sdf")),
#         library=str(datadir.join("shapeit/Enamine_FDA_646cpds_3D_prepared.sdf")),
#     ).run()

#     expected_files = ["fda_against_aspirin.sdf"]
#     for expf in expected_files:
#         assert os.path.exists(
#             os.path.join(outdir, expf)
#         ), f"Could not find {os.path.join(outdir, expf)}"


# def _test_kdeep(datadir):
#     from playmolecule import apps

#     outdir, scratchdir = prepare(datadir)
#     apps.kdeep.v1(
#         outdir=outdir,
#         scratchdir=scratchdir,
#         pdb=str(datadir.join("kdeep/10gs_protein.pdb")),
#         sdf=str(datadir.join("kdeep/10gs_ligand.sdf")),
#         modelfile=str(datadir.join("kdeep/default.ckpt")),
#         correlation_field="EXP_AFF",
#     ).run()

#     expected_files = [
#         "0_10gs_ligand_processed.sdf",
#         "1_10gs_ligand_fake_copy_processed.sdf",
#         "config.nap",
#         "pearson.png",
#         "processed.sdf",
#         "protein.pdb",
#         "results.csv",
#         "web_content.pickle",
#     ]
#     for expf in expected_files:
#         assert os.path.exists(
#             os.path.join(outdir, expf)
#         ), f"Could not find {os.path.join(outdir, expf)}"


# def _test_aceprep(datadir):
#     from playmolecule import apps

#     outdir, scratchdir = prepare(datadir)
#     apps.aceprep.v1(
#         outdir=outdir,
#         scratchdir=scratchdir,
#         ligands=str(datadir.join("aceprep/ligands.smi")),
#         create_table=True,
#     ).run()

#     expected_files = [
#         "ligands",
#         "plots",
#         "prepared_ligands.log",
#         "prepared_ligands.sdf",
#         "prepared_ligands.xlsx",
#         "table.pkl",
#     ]
#     for expf in expected_files:
#         assert os.path.exists(
#             os.path.join(outdir, expf)
#         ), f"Could not find {os.path.join(outdir, expf)}"


# def _test_acesearch(datadir):
#     from playmolecule.apps import acesearch

#     outdir, _ = prepare(datadir)
#     acesearch.v1(
#         outdir=outdir,
#         outname="queryoutsmarts22.csv",
#         smiles=None,
#         smarts="[OX2H][cX3]:[c]",
#         limitN=9,
#         sim_cutoff=0.5,
#         substruc_search=True,
#     ).run()

#     expected_files = ["queryoutsmarts22.csv"]
#     for expf in expected_files:
#         assert os.path.exists(
#             os.path.join(outdir, expf)
#         ), f"Could not find {os.path.join(outdir, expf)}"
