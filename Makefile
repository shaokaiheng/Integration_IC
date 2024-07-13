IN_FILE_LST := /home/ICer/ic_prjs/E203_vcs/E203_vcs/rtl/e203/soc/e203_soc_top.v \
				/home/ICer/ic_prjs/E203_vcs/E203_vcs/rtl/e203/perips/sirv_pmu.v \
				/home/ICer/ic_prjs/E203_vcs/E203_vcs/rtl/e203/perips/sirv_queue_1.v \
				/home/ICer/ic_prjs/E203_vcs/E203_vcs/rtl/e203/perips/apb_i2c/apb_i2c.v \
				/home/ICer/ic_prjs/E203_vcs/E203_vcs/rtl/e203/perips/apb_i2c/i2c_master_byte_ctrl.v
print_all_in_file:
	$(foreach item,$(IN_FILE_LST),$(info Please Confirm Input File: $(item)))

create_in_dir:
	@if [ ! -d 'input_file' ]; then \
		echo "Directory input_file does not exist, creating..."; \
		mkdir -p 'input_file'; \
	fi
	
copy_file:
	$(foreach item,$(IN_FILE_LST),$(shell cp -r '$(item)' 'input_file/'))
	@echo "Copying All Input_files into dir.. "

clean_tmp:
	rm -rf ./input_file

run:clean_tmp print_all_in_file create_in_dir copy_file
