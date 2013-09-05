make_webfront := cc

default:
	@echo Targets:
	@echo "deploy"
	@echo "css - run less to generate output css files"
	@echo

deploy:
	@echo "Stub!"

css:
	$(make_webfront)/compile-styles.sh


# vim: sw=8 ts=8 noet:
