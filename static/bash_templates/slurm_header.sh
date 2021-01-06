#!/bin/bash

#SBATCH -A SISTR
#SBATCH -J {{token}}
#SBATCH -o tmp/{{token}}/slurm-%x.out.txt
#SBATCH -t 0:30:00
#SBATCH -p sistr
#SBATCH -n 1

inputfilepaths=(
 {{input_filepaths}}
)


for input_filename in ${inputfilepaths[@]};do
    output_file_name=$(basename -- ${input_filename})
    command="sistr -i ${input_filename} ${output_file_name} -f csv -o tmp/{{token}}/${output_file_name}"
    echo $(sistr -V) && echo $command
    eval $command
done

mkdir -p results/{{token}} tmp/{{token}} &&
mv tmp/{{token}}/*.csv tmp/{{token}}/*.txt  results/{{token}}/ &&
rm -rf tmp/{{token}}
{{send_email}}