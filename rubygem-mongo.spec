%{?scl:%scl_package rubygem-%{gem_name}}
%{!?scl:%global pkg_name %{name}}

%global gem_name mongo

# Enable test when building on local.
%global enable_tests 0

%if 0%{?enable_tests}
# Fallback to rh-mongodb36. rh-mongodb36-scldevel is probably not available in
# the buildroot.
%{?scl:%{!?scl_mongodb:%global scl_mongodb rh-mongodb36}}
%{?scl:%{!?scl_prefix_mongodb:%global scl_prefix_mongodb %{scl_mongodb}-}}
%endif

Name:          %{?scl_prefix}rubygem-%{gem_name}
Version:       2.5.1
Release:       1.bs1%{?dist}
Summary:       Ruby driver for MongoDB
Group:         Development/Languages
License:       ASL 2.0
URL:           http://www.mongodb.org
Source0:       https://rubygems.org/gems/%{gem_name}-%{version}.gem
# Sources for rspec to test internally.
# Enable lines of Source code when testing on local. Don't import those.
# Source200: diff-lcs-1.3.gem
# Source201: rspec-3.7.0.gem
# Source202: rspec-core-3.7.0.gem
# Source203: rspec-expectations-3.7.0.gem
# Source204: rspec-mocks-3.7.0.gem
# Source205: rspec-support-3.7.0.gem

Requires:      %{?scl_prefix}ruby(release)
Requires:      %{?scl_prefix}ruby(rubygems)
Requires:      %{?scl_prefix}rubygem(bson) >= 4.3.0
BuildRequires: %{?scl_prefix}ruby(release)
BuildRequires: %{?scl_prefix}ruby(rubygems)
BuildRequires: %{?scl_prefix}ruby
BuildRequires: %{?scl_prefix}rubygems-devel
%if 0%{?enable_tests}
# For running the tests
BuildRequires: %{?scl_prefix_mongodb}mongodb-server
BuildRequires: %{?scl_prefix}rubygem(bson) >= 4.3.0
%endif
BuildArch:     noarch
Provides:      %{?scl_prefix}rubygem(%{gem_name}) = %{version}

%description
A Ruby driver for MongoDB.

%package doc
Summary: Documentation for %{pkg_name}
Group: Documentation
Requires:%{?scl_prefix}%{pkg_name} = %{version}-%{release}
BuildArch: noarch

%description doc
Documentation for %{pkg_name}.

%prep
%{?scl:scl enable %{scl} - << \EOF}
set -ex
gem unpack %{SOURCE0}

%setup -q -D -T -n  %{gem_name}-%{version}

gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec
%{?scl:EOF}

%build
# Create the gem as gem install only works on a gem file
%{?scl:scl enable %{scl} - << \EOF}
set -ex
gem build %{gem_name}.gemspec
%gem_install
%{?scl:EOF}

%install
mkdir -p %{buildroot}%{gem_dir}
cp -a .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/


mkdir -p %{buildroot}%{_bindir}
cp -a .%{_bindir}/* \
        %{buildroot}%{_bindir}/

find %{buildroot}%{gem_instdir}/bin -type f | xargs chmod a+x

# Drop the shebang, file is not executable anyway.
sed -i '/#!\// d' %{buildroot}%{gem_instdir}/Rakefile

%if 0%{?enable_tests}
%check
%{?scl:scl enable %{scl} %{scl_mongodb} - << \EOF}
set -ex
pushd .%{gem_instdir}

# mkdir gems
# pushd gems
# cp -p "%%{SOURCE200}" .
# cp -p "%%{SOURCE201}" .
# cp -p "%%{SOURCE202}" .
# cp -p "%%{SOURCE203}" .
# cp -p "%%{SOURCE204}" .
# cp -p "%%{SOURCE205}" .
# gem install *.gem --local --no-document
# # Path to rspec is not set in Copr.
# export PATH="~/bin:${PATH}"
# popd

# Create data directory and start testing mongo instance.
# See https://github.com/mongodb/mongo-ruby-driver/blob/master/.travis.yml
mkdir data
mongod \
  --dbpath data \
  --logpath data/log \
  --fork \
  --auth

CI=1 EXTERNAL_DISABLED=1 rspec spec

# Shutdown mongo and cleanup the data.
mongod --shutdown --dbpath data
rm -rf data
popd
%{?scl:EOF}
%endif

%files
%dir %{gem_instdir}
%{_bindir}/mongo_console
%license %{gem_instdir}/LICENSE
%{gem_instdir}/bin
%{gem_libdir}
%exclude %{gem_instdir}/mongo.gemspec
%exclude %{gem_cache}
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/CONTRIBUTING.md
%doc %{gem_instdir}/README.md
%{gem_instdir}/Rakefile
%{gem_instdir}/spec

%changelog
* Mon Feb 26 2018 Jun Aruga <jaruga@redhat.com> - 2.5.1-1
- Update to mongo 2.5.1.

* Fri Feb 16 2018 Jun Aruga <jaruga@redhat.com> - 2.5.0-1
- Update to mongo 2.5.0.
- Escape macros in %%changelog

* Thu Feb 15 2018 Jun Aruga <jaruga@redhat.com> - 2.4.3-2
- Update mongodb SCL used in tests to rh-mongodb36.

* Mon Dec 18 2017 Jun Aruga <jaruga@redhat.com> - 2.4.3-1
- Update to mongo 2.4.3.

* Thu Jan 19 2017 Jun Aruga <jaruga@redhat.com> - 2.4.1-1
- Update to mongo 2.4.1.

* Mon Apr 18 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-5
- Use rspec tests

* Tue Apr 12 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-4
- Fix Fix missing wrapper for mongo_console executable
  - Resolves: rhbz#1315283

* Wed Apr 06 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-3
- Add rubygem-shoulda to BuildReqires (for tests)

* Wed Apr 06 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-2
- Enable tests

* Mon Feb 29 2016 Pavel Valena <pvalena@redhat.com> - 2.2.3-1
- Update to 2.2.3

* Tue Feb 16 2016 Troy Dawson <tdawson@redhat.com> - 1.10.2-5
- Disable tests until mongodb becomes stable in rawhide again.

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Mon Jul 27 2015 Troy Dawson <tdawson@redhat.com> - 1.10.2-2
- Fix tests

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.10.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Thu Jun 26 2014 Vít Ondruch <vondruch@redhat.com> - 1.10.2-1
- Update to mongo 1.10.2.

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Nov 19 2013 Vít Ondruch <vondruch@redhat.com> - 1.9.2-1
- Update to mongo 1.9.2.
- Enabled test suite.

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.4-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Mar 13 2013 Troy Dawson <tdawson@redhat.com> - 1.6.4-4
- Fix to make it build/install on F19+

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.6.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Aug 10 2012 Troy Dawson <tdawson@redhat.com> - 1.6.4-2
- Fixed doc
- removed more BuildRequires that are not required

* Thu Aug 09 2012 Troy Dawson <tdawson@redhat.com> - 1.6.4-1
- Updated to latest version
- Removed BuildRequires that are not needed

* Thu Aug 09 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-7
- Fixed checks.  
  Only run checks that do not require a running mongodb server

* Tue Aug 07 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-6
- Changed .gemspec and Rakefile to not be doc
- Added checks

* Thu Aug 02 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-5
- Fixed rubygem(bson) requires

* Mon Jul 23 2012 Troy Dawson <tdawson@redhat.com> - 1.4.0-4
- Updated to meet new fedora rubygem guidelines

* Thu Nov 17 2011 Troy Dawson <tdawson@redhat.com> - 1.4.0-3
- Changed group to Development/Languages
- Changed the global variables
- Seperated the doc and test into the doc rpm

* Thu Nov 17 2011 Troy Dawson <tdawson@redhat.com> - 1.4.0-2
- Added %.bs1%{?dist} to version

* Tue Nov 15 2011  <tdawson@redhat.com> - 1.4.0-1
- Initial package
