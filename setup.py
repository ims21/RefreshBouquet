from distutils.core import setup
import setup_translate

pkg = 'Extensions.RefreshBouquet'
setup(name='enigma2-plugin-extensions-refreshbouquet',
	version='2.13',
	description='actualize services in bouquets',
	packages=[pkg],
	package_dir={pkg: 'plugin'},
	package_data={pkg: ['*.png', '*.xml', '*/*.png', 'locale/*.pot', 'locale/*/LC_MESSAGES/*.mo', 'rbb/*.rbb']},
	cmdclass=setup_translate.cmdclass, # for translation
	)
