from distutils.core import setup
import setup_translate

pkg = 'Extensions.RefreshBouquet'
setup (name = 'enigma2-plugin-extensions-refreshbouquet',
       version = '1.44',
       description = 'actualize services in bouquets',
       packages = [pkg],
       package_dir = {pkg: 'plugin'},
       package_data = {pkg: ['*.png', '*.xml', 'locale/*.pot', 'locale/*/LC_MESSAGES/*.mo']},
       cmdclass = setup_translate.cmdclass, # for translation
      )
