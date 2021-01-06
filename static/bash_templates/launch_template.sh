#!/bin/bash


#source activate sistr

inputfilepaths=(
 {{input_filepaths}}
)


for input_filename in ${inputfilepaths[@]};do
    output_file_name=$(basename -- ${input_filename})
    sistr -i ${input_filename} ${output_file_name} -f csv -o tmp/{{token}}/${output_file_name} &>> tmp/{{token}}/run_log.txt
done

mkdir -p results/{{token}} tmp/{{token}} &&
mv tmp/{{token}}/*.csv tmp/{{token}}/*.txt  results/{{token}}/ &&
rm tmp/{{token}}

