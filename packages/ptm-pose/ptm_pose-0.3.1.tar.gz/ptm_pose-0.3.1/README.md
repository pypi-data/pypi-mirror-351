# PTM-POSE (PTM Projection Onto Splice Events)

*[Full documentation](https://naeglelab.github.io/PTM-POSE/)*

PTM-POSE is an easily implementable tool to project PTM sites onto splice event data generated from RNA sequencing data and is compatible with any splice event quantification tool that outputs genomic coordinates of different splice events (MATS, SpliceSeq, etc.). PTM-POSE harnesses PTMs that have been mapped to their genomic location by a sister package, [ExonPTMapper](https://github.com/NaegleLab/ExonPTMapper). It also contains functions for annotating these PTMs with information from various databases, like PhosphoSitePlus and ELM.

![PTM-POSE method for projecting PTMs onto splice events](./figures/method.png)

## Running PTM-POSE

To run PTM-POSE, you first need to process your data such that each row corresponds to a unique splice event with the genomic location of that splice event (chromosome, strand, and the bounds of the spliced region). Strand can be indicated using either '+'/'-' or 1/-1. If desired, you can also provide a delta PSI and significance value which will be included in the final PTM dataframe. Any additional columns will be kept. At a minimum, the dataframe should look something like this (optional but recommended parameters indicated):
| event_id (optional) | Gene name (recommend) | chromosome | strand | region_start | region_end | dPSI (optional) | significance (optional) |
|---------------------|-----------------------|------------|--------|--------------|------------|-----------------|-------------------------|
| first_event         | CSTN1                 |1           |  -     | 9797555      | 9797612    | 0.362           | 0.032                   |

 Once the data is in the correct format, simply run the project_ptms_onto_splice_events() function. By default, PTM-POSE assumes the provided coordinates are in hg38 coordinates, but you can use older coordinate systems with the `coordinate_type` parameter.
```python
from ptm-pose import project

my_splice_data_annotated, spliced_ptms = project.project_ptms_onto_splice_events(my_splice_data, ptm_coordinates,
                                                                                  chromosome_col = 'chromosome',
                                                                                  strand_col = 'strand',
                                                                                  region_start_col = 'region_start',
                                                                                  region_end_col =  'region_end',
                                                                                  event_id_col = 'event_id',
                                                                                  gene_col = 'Gene name',
                                                                                  dPSI_col='dPSI',
                                                                                  coordinate_type = 'hg19')
```
## Altered Flanking Sequences

In addition to the previously mentioned columns, we will need to know the location of the flanking exonic regions next to the spliced region. Make sure your dataframe contains the following information prior to running flanking sequence analysis:
| event_id (optional) | Gene name (recommended) | chromosome | strand | region_start | region_end | first_flank_start | first_flank_end | second_flank_start | second_flank_end |dPSI (optional) | significance (optional) |
|---------------------|-------------------------|------------|--------|--------------|------------|-------------------|-----------------|--------------------|------------------|----------------|-------------------------|
| first_event         |  CSTN1                  |1           |  -     | 9797555      | 9797612    | 9687655           | 9688446         | 9811223            | 9811745          |0.362           | 0.032                   |


Then, as with differentially included PTMs, you only need to run `get_flanking_changes_from_splice_data()` function:

```python
from ptm-pose import project

altered_flanks = project.get_flanking_changes_from_splice_data(my_splice_data, ptm_coordinates,
                                                                                  chromosome_col = 'chromosome',
                                                                                  strand_col = 'strand',
                                                                                  region_start_col = 'region_start',
                                                                                  region_end_col =  'region_end',
                                                                                  first_flank_start_col = 'first_flank_start',
                                                                                  first_flank_end_col = 'first_flank_end',
                                                                                  second_flank_start_col = 'second_flank_start',
                                                                                  second_flank_end_col = 'second_flank_start',
                                                                                  event_id_col = 'event_id',
                                                                                  gene_col = 'Gene name',
                                                                                  dPSI_col='dPSI',
                                                                                  coordinate_type = 'hg19')
```

## Downstream Analysis

PTM-POSE also provides functions in the `annotate` module for annotating the above outputs with functional information from various databases: PhosphoSitePlus, RegPhos, PTMcode, PTMInt, ELM, DEPOD, OmniPath, and PTMsigDB. You can then identify PTMs with specific functions, interaction, etc. with the `analyze` module. For more information and examples of analysis, see the [full documentation](https://naeglelab.github.io/PTM-POSE/).


## Have questions?

Please reach out to Sam Crowl (sc8wf@virginia.edu) if you have questions or suggestions about new analysis functions that you would like to see implemented. We hope to continue to expand the analysis that can be easily performed with this package as time goes on, and welcome any feedback.

